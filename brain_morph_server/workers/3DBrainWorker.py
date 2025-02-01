import os
import trimesh
import numpy as np
import nibabel as nib
from scipy.ndimage import gaussian_filter
from vedo import Volume, merge
from concurrent.futures import ThreadPoolExecutor
from engine.conf.Worker import Worker
from engine.models import FailedTask, Task
from brain_morph_server import models


class ThreeDBrainWorker(Worker):
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
        patient: models.Patient = task.job_payload.patient

        nii_file = patient.nii_file_path

        with ThreadPoolExecutor() as executor:
            future = executor.submit(
                self.visualize_and_color_combined_mesh,
                nii_file, parent_folder, str(patient.folder_name), patient=patient
            )
            future.result()

    def export_to_gltf(self, mesh, export_path, filename, colors, opacity=1.0):
        vertices = np.array(mesh.vertices, dtype=np.float32)
        faces = np.array(mesh.cells, dtype=np.int32)
        colors = np.array(colors, dtype=np.uint8)

        colors = colors / 255.0

        tri_mesh = trimesh.Trimesh(
            vertices=vertices, faces=faces, process=False)
        tri_mesh.visual.vertex_colors = colors

        material = trimesh.visual.material.PBRMaterial(
            baseColorFactor=[1.0, 1.0, 1.0, opacity],
            alphaMode="BLEND",
        )
        tri_mesh.visual.material = material

        gltf_path = os.path.join(export_path, filename)
        tri_mesh.export(gltf_path, file_type="glb")
        print(f"Exported GLTF: {gltf_path}")

    def visualize_and_color_combined_mesh(self, file_path, export_path, file_id, patient: models.Patient = None):
        os.makedirs(export_path, exist_ok=True)

        nii_data = nib.load(file_path)
        voxel_spacing = nii_data.header.get_zooms()[:3]
        volume_data = nii_data.get_fdata()

        if volume_data.ndim == 4:
            print("4D data detected, selecting the first channel.")
            volume_data = volume_data[..., 0]

        normalized_data = (volume_data - volume_data.min()) / \
            (volume_data.max() - volume_data.min())
        smoothed_data = gaussian_filter(normalized_data, sigma=1.0)

        volume = Volume(smoothed_data)
        volume.spacing(voxel_spacing)

        brain_mesh = volume.isosurface(value=0.1).color('gray').opacity(0.85)
        tumor_mesh = volume.isosurface(value=0.6).color('red').opacity(1.0)

        brain_colors = np.full((len(brain_mesh.vertices), 4), [
                               128, 128, 128, int(0.85 * 255)], dtype=np.uint8)
        tumor_colors = np.full((len(tumor_mesh.vertices), 4), [
                               255, 0, 0, 255], dtype=np.uint8)

        brain_export = f"brain_{file_id}.glb"
        self.export_to_gltf(brain_mesh, export_path,
                            brain_export, brain_colors, opacity=0.9)
        patient.brain_file_path = os.path.join(export_path, brain_export)

        tumor_export = f"tumor_{file_id}.glb"
        self.export_to_gltf(tumor_mesh, export_path,
                            tumor_export, tumor_colors, opacity=1.0)
        patient.tumor_file_path = os.path.join(export_path, tumor_export)

        combined_mesh = merge(brain_mesh, tumor_mesh)

        combined_colors = np.full((len(combined_mesh.vertices), 4), [
                                  128, 128, 128, int(0.9 * 255)], dtype=np.uint8)

        tumor_start_index = len(brain_mesh.vertices)
        combined_colors[tumor_start_index:] = [255, 0, 0, 255]

        brain_3d = f"brain_3D_{file_id}.glb"

        self.export_to_gltf(combined_mesh, export_path,
                            brain_3d, combined_colors, opacity=0.8)
        patient.brain_combine_file_path = os.path.join(
            export_path, brain_3d)

        patient.save(update_fields=[
                     'brain_combine_file_path', 'tumor_file_path', 'brain_file_path'])
        return (brain_3d, brain_export, tumor_export)
