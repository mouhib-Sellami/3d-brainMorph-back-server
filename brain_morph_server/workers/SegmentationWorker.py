import os
import numpy as np
import nibabel as nib
from skimage import io
from natsort import natsorted
from engine.conf.Worker import Worker
from engine.models import FailedTask, Task
from brain_morph_server import models
from brain_morph_server import views
from brainMorph_back_server.model import brain_morph_model
from collections import defaultdict
from scipy.ndimage import gaussian_filter


class SegmentationWorker(Worker):
    def on_exception_callback(self, task: Task, exception: Exception):
        super().on_exception_callback(task, exception)

    def on_failed_callback(self, failed_task: FailedTask, exception: Exception):
        job: models.JobClientArtifact = failed_task.task.job_payload
        patient: models.Patient = job.patient
        patient.is_processing = False
        patient.save(update_fields=['is_processing'])
        super().on_failed_callback(failed_task, exception)

    def on_finish_callback(self, task: Task):
        super().on_finish_callback(task)

    def worker_runner(self, task: Task):
        super().worker_runner(task)
        parent_folder = task.job_payload.download_folder_path

        files = [os.path.join(parent_folder, x) for x in os.listdir(
            task.job_payload.download_folder_path) if "mask" not in x]

        for f in files:
            brain_morph_model.predict_save_image(f, views.model)

        output_nii = self.process_images(
            parent_folder, parent_folder, 1.0, 1.0)

        patient: models.Patient = task.job_payload.patient
        patient.nii_file_path = output_nii
        patient.save(update_fields=['nii_file_path'])

        views.engine_process_brain.add_task(
            task=task, new=True, delete_when_finish=False)

    def load_images(self, image_dir):
        grouped_slices = defaultdict(lambda: {"brain": [], "mask": []})

        file_list = natsorted(
            [f for f in os.listdir(image_dir) if f.endswith('.tif')])
        for file in file_list:
            unique_id, file_type = file.split(
                '_')[2], "mask" if "mask" in file else "brain"
            img_path = os.path.join(image_dir, file)
            img = io.imread(img_path)
            grouped_slices[unique_id][file_type].append(img)
            print("*"*100)
            print(file)

        return grouped_slices

    def create_combined_volume(self, brain_slices, mask_slices):
        brain_volume = np.stack(brain_slices, axis=0).astype(np.float32)
        mask_volume = np.stack(mask_slices, axis=0).astype(np.uint8)
        print(mask_volume.argmax())
        brain_volume = (brain_volume / brain_volume.max()) * 255
        combined_volume = brain_volume.copy()
        combined_volume[mask_volume > 0] = 255
        return combined_volume

    def save_as_nii(self, volume, filename, export_path, x_spacing=1.0, y_spacing=1.0, z_spacing=1.0):
        affine = np.eye(4)
        affine[0, 0] = x_spacing
        affine[1, 1] = y_spacing
        affine[2, 2] = z_spacing

        nii_img = nib.Nifti1Image(volume, affine)

        os.makedirs(export_path, exist_ok=True)
        full_path = os.path.join(export_path, filename)
        nib.save(nii_img, full_path)
        print(
            f"Saved 3D NIfTI file: {full_path} with spacing: x={x_spacing}, y={y_spacing}, z={z_spacing} mm")

    def get_x_spacing(self, num_slices):
        if num_slices < 25:
            return 3.0
        elif num_slices <= 35:
            return 2.3
        elif num_slices <= 72:
            return 1.8
        else:
            return 1.6

    def smooth_volume(self, volume, sigma=1.0):
        return gaussian_filter(volume, sigma=sigma)

    def process_images(self, image_dir, export_path, y_spacing=1.0, z_spacing=1.0):
        grouped_slices = self.load_images(image_dir)

        for unique_id, data in grouped_slices.items():
            brain_slices = data["brain"]
            mask_slices = data["mask"]

            if len(brain_slices) != len(mask_slices):
                print(
                    f"Mismatch in slices for ID {unique_id}: {len(brain_slices)} brain vs {len(mask_slices)} mask")
                continue
            combined_volume = self.create_combined_volume(
                brain_slices, mask_slices)

            combined_volume = self.smooth_volume(combined_volume, sigma=1.0)

            num_slices = len(brain_slices)
            x_spacing = self.get_x_spacing(num_slices)

            nii_filename = f"brain_3D_{unique_id}.nii"
            self.save_as_nii(combined_volume, nii_filename,
                             export_path, x_spacing, y_spacing, z_spacing)
            return os.path.join(export_path, nii_filename)
