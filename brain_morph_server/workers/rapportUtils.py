import os
import numpy as np
from vedo import Plotter, Axes
from fpdf import FPDF
from fpdf.enums import XPos, YPos


def sanitize_text(text):
    replacements = {
        "\u2018": "'",
        "\u2019": "'",
        "\u201c": '"',
        "\u201d": '"',
        "\u2013": "-",
        "\u2014": "-",
    }
    for orig, repl in replacements.items():
        text = text.replace(orig, repl)
    return text


def calculate_mesh_info(mesh):
    if mesh is None:
        return {"width": 0, "height": 0, "depth": 0, "centroid": (0, 0, 0), "surface_area": 0}
    b = mesh.bounds()
    centroid = mesh.center_of_mass()
    surface_area = mesh.area()
    return {
        "width": b[1] - b[0],
        "height": b[3] - b[2],
        "depth": b[5] - b[4],
        "centroid": centroid,
        "surface_area": surface_area
    }


def capture_view(meshes, filename, camera_position, focal_point, viewup=(0, 1, 0), size=(1500, 1500)):
    plt = Plotter(offscreen=True, size=size)

    for m in meshes:
        plt.add(m)

    axes = Axes(meshes[0], c='black', xtitle='X (mm)',
                ytitle='Y (mm)', ztitle='Z (mm)')
    plt.add(axes)

    plt.camera.SetPosition(camera_position)
    plt.camera.SetFocalPoint(focal_point)
    plt.camera.SetViewUp(viewup)

    plt.show(interactive=False)
    plt.screenshot(filename)
    plt.close()


def calculate_tumor_volume(width, height, depth):
    return (4/3) * np.pi * (width/2) * (height/2) * (depth/2)


def estimate_tumor_mass(volume_mm3):
    volume_cm3 = volume_mm3 * 1e-3
    return volume_cm3 * 1.05


def get_anatomical_localization(centroid, voxel_spacing=(1, 1, 1)):
    x, y, z = centroid
    regions = []

    if z > 0:
        regions.append("Frontal Lobe")
        if y < 40:
            regions.append("Prefrontal Cortex")
        if 40 < y < 70:
            regions.append("Primary Motor Cortex (Brodmann Area 4)")

    if z < 0:
        regions.append("Temporal Lobe")
        if x > 50:
            regions.append(
                "Wernicke's Area (Left Hemisphere)" if x > 0 else "Heschl's Gyrus")

    if y > 70:
        regions.append("Parietal Lobe")
        if z > 30:
            regions.append("Somatosensory Cortex")
    elif y < 30:
        regions.append("Occipital Lobe (Visual Cortex)")

    if abs(x) < 20 and 20 < y < 60 and z < 20:
        regions.append("Basal Ganglia/Thalamus")
    if abs(z) < 10 and y < 30:
        regions.append("Brainstem (Midbrain/Pons)")

    implications = []
    if "Primary Motor Cortex" in regions:
        implications.append(
            "Potential motor function deficits (weakness, paralysis)")
    if "Wernicke's Area" in regions:
        implications.append("Possible language comprehension impairment")
    if "Brainstem" in regions:
        implications.append(
            "Critical location: May affect vital functions (respiration, heart rate)")
    if "Visual Cortex" in regions:
        implications.append("Risk of visual field defects")

    return {
        "regions": regions,
        "implications": implications,
        "critical_risk": "High" if "Brainstem" in regions else "Moderate"
    }


def generate_pdf_report(file_id, brain_mesh, tumor_mesh, export_path, patient_code='90477c65-3c70-4867-85a6-2b'):
    os.makedirs(export_path, exist_ok=True)

    brain_info = calculate_mesh_info(brain_mesh)
    tumor_info = calculate_mesh_info(tumor_mesh)

    tumor_front_img = os.path.join(export_path, f"tumor_front_{file_id}.png")
    tumor_left_img = os.path.join(export_path, f"tumor_left_{file_id}.png")
    tumor_top_img = os.path.join(export_path, f"tumor_top_{file_id}.png")
    tumor_right_img = os.path.join(export_path, f"tumor_right_{file_id}.png")

    overlay_front_img = os.path.join(
        export_path, f"overlay_front_{file_id}.png")
    overlay_left_img = os.path.join(export_path, f"overlay_left_{file_id}.png")
    overlay_top_img = os.path.join(export_path, f"overlay_top_{file_id}.png")
    overlay_right_img = os.path.join(
        export_path, f"overlay_right_{file_id}.png")

    qr_path = os.path.join(os.path.dirname(__file__), "qrcode.png")

    cx_tumor, cy_tumor, cz_tumor = tumor_info["centroid"]
    d_tumor = max(tumor_info["width"],
                  tumor_info["height"], tumor_info["depth"]) * 3

    tumor_clone_red = tumor_mesh.clone().color("red")
    capture_view([tumor_clone_red], tumor_front_img, (cx_tumor, cy_tumor -
                 d_tumor, cz_tumor), tumor_info["centroid"], size=(1000, 1000))
    capture_view([tumor_clone_red], tumor_left_img, (cx_tumor - d_tumor,
                 cy_tumor, cz_tumor), tumor_info["centroid"], size=(1000, 1000))
    capture_view([tumor_clone_red], tumor_top_img, (cx_tumor, cy_tumor,
                 cz_tumor + d_tumor), tumor_info["centroid"], size=(1000, 1000))
    capture_view([tumor_clone_red], tumor_right_img, (cx_tumor + d_tumor,
                 cy_tumor, cz_tumor), tumor_info["centroid"], size=(1000, 1000))

    cx_brain, cy_brain, cz_brain = brain_info["centroid"]
    d_brain = max(brain_info["width"],
                  brain_info["height"], brain_info["depth"]) * 3

    brain_clone = brain_mesh.clone()
    tumor_clone_red_overlay = tumor_mesh.clone().color("red")
    brain_clone.alpha(0.2)
    brain_clone.color('gray')

    capture_view([brain_clone, tumor_clone_red_overlay], overlay_front_img, (cx_brain,
                 cy_brain - d_brain, cz_brain), brain_info["centroid"], size=(1000, 1000))
    capture_view([brain_clone, tumor_clone_red_overlay], overlay_left_img, (cx_brain -
                 d_brain, cy_brain, cz_brain), brain_info["centroid"], size=(1000, 1000))
    capture_view([brain_clone, tumor_clone_red_overlay], overlay_top_img, (cx_brain,
                 cy_brain, cz_brain + d_brain), brain_info["centroid"], size=(1000, 1000))
    capture_view([brain_clone, tumor_clone_red_overlay], overlay_right_img, (cx_brain +
                 d_brain, cy_brain, cz_brain), brain_info["centroid"], size=(1000, 1000))

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)

    from datetime import datetime

    pdf.add_page()
    pdf.ln(20)

    pdf.set_text_color(255, 59, 0)
    pdf.set_font("Times", 'B', 34)
    pdf.cell(0, 24, "BrainMorph AI", new_x=XPos.LMARGIN,
             new_y=YPos.NEXT, align="C")

    pdf.set_text_color(117, 85, 85)
    pdf.set_font("Times", 'B', 26)
    pdf.cell(0, 18, "Brain Tumor Analysis Report",
             new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")

    pdf.ln(5)
    pdf.set_draw_color(255, 59, 0)
    pdf.line(60, pdf.get_y(), 150, pdf.get_y())
    pdf.ln(15)

    pdf.set_text_color(27, 28, 29)
    pdf.set_font("Times", 'B', 18)
    pdf.cell(0, 12, "Patient Details", new_x=XPos.LMARGIN,
             new_y=YPos.NEXT, align="C")

    pdf.set_font("Times", size=14)
    pdf.multi_cell(0, 8, sanitize_text(
        f"Patient Identifier: {patient_code}"), align="C")

    pdf.ln(15)

    pdf.image(qr_path, x=(210 - 100) / 2, w=100, h=100)
    pdf.ln(15)

    pdf.set_y(-40)

    report_date = datetime.now().strftime("%B %d, %Y")
    pdf.set_font("Times", 'I', 12)
    pdf.cell(0, 10, f"Report Date: {report_date}",
             new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")

    pdf.ln(2)

    pdf.set_font("Times", 'I', 10)
    pdf.cell(0, 10, "This report is automatically generated, consult a medical professional for analysis.",
             new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
    pdf.set_text_color(0, 0, 0)
    pdf.set_draw_color(0, 0, 0)

    pdf.add_page()
    pdf.set_font("Helvetica", 'B', 16)
    pdf.cell(
        0, 10, f"Tumor Multi-View Projections", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
    pdf.ln(10)

    positions = [(15, 30), (110, 30), (15, 120), (110, 120)]
    image_width = 90
    image_height = 60

    projections = [tumor_top_img, tumor_front_img,
                   tumor_left_img, tumor_right_img]
    labels = ["Top View", "Front View", "Left View", "Right View"]

    for i, (img, pos, label) in enumerate(zip(projections, positions, labels)):
        x, y = pos
        pdf.image(img, x=x, y=y, w=image_width, h=image_height)
        pdf.set_xy(x, y + image_height + 3)
        pdf.set_font("Helvetica", 'B', size=10)
        pdf.cell(image_width, 8, sanitize_text(f"{label}: Tumor"), align="C")
        pdf.ln(5)

    pdf.ln(10)

    table_width = 90
    col1_width = 40
    col2_width = 50
    table_x = (pdf.w - table_width) / 2

    pdf.set_xy(table_x, pdf.get_y())
    pdf.set_font("Helvetica", 'B', 12)
    pdf.cell(col1_width, 10, "Dimension", border=1, align="C")
    pdf.cell(col2_width, 10, "Value (mm)", border=1, align="C")
    pdf.ln()

    pdf.set_font("Helvetica", size=10)
    pdf.set_x(table_x)
    pdf.cell(col1_width, 10, "Width", border=1, align="C")
    pdf.cell(col2_width, 10, f"{tumor_info['width']:.2f}", border=1, align="C")
    pdf.ln()
    pdf.set_x(table_x)
    pdf.cell(col1_width, 10, "Height", border=1, align="C")
    pdf.cell(col2_width, 10,
             f"{tumor_info['height']:.2f}", border=1, align="C")
    pdf.ln()
    pdf.set_x(table_x)
    pdf.cell(col1_width, 10, "Depth", border=1, align="C")
    pdf.cell(col2_width, 10, f"{tumor_info['depth']:.2f}", border=1, align="C")
    pdf.ln()

    pdf.set_x(table_x)
    pdf.cell(col1_width, 10, "Centroid Coordinates", border=1, align="C")
    pdf.cell(col2_width, 10,
             f"({tumor_info['centroid'][0]:.2f}, {tumor_info['centroid'][1]:.2f}, {tumor_info['centroid'][2]:.2f})", border=1, align="C")
    pdf.ln()
    pdf.set_x(table_x)
    pdf.cell(col1_width, 10, "Surface Area", border=1, align="C")
    pdf.cell(col2_width, 10,
             f"{tumor_info['surface_area']:.2f} mm²", border=1, align="C")
    pdf.ln()

    pdf.add_page()
    pdf.set_font("Helvetica", 'B', 16)
    pdf.cell(
        0, 10, f"Brain with Tumor Overlay Multi-View Projections", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
    pdf.ln(10)

    projections = [overlay_top_img, overlay_front_img,
                   overlay_left_img, overlay_right_img]
    labels = ["Top View", "Front View", "Left View", "Right View"]

    for i, (img, pos, label) in enumerate(zip(projections, positions, labels)):
        x, y = pos
        pdf.image(img, x=x, y=y, w=image_width, h=image_height)
        pdf.set_xy(x, y + image_height + 3)
        pdf.set_font("Helvetica", 'B', size=10)
        pdf.cell(image_width, 8, sanitize_text(
            f"{label}: Brain with Tumor"), align="C")
        pdf.ln(5)

    pdf.ln(10)

    pdf.set_xy(table_x, pdf.get_y())
    pdf.set_font("Helvetica", 'B', 12)
    pdf.cell(col1_width, 10, "Dimension", border=1, align="C")
    pdf.cell(col2_width, 10, "Value (mm)", border=1, align="C")
    pdf.ln()

    pdf.set_font("Helvetica", size=10)
    pdf.set_x(table_x)
    pdf.cell(col1_width, 10, "Width", border=1, align="C")
    pdf.cell(col2_width, 10, f"{brain_info['width']:.2f}", border=1, align="C")
    pdf.ln()
    pdf.set_x(table_x)
    pdf.cell(col1_width, 10, "Height", border=1, align="C")
    pdf.cell(col2_width, 10,
             f"{brain_info['height']:.2f}", border=1, align="C")
    pdf.ln()
    pdf.set_x(table_x)
    pdf.cell(col1_width, 10, "Depth", border=1, align="C")
    pdf.cell(col2_width, 10, f"{brain_info['depth']:.2f}", border=1, align="C")
    pdf.ln()

    pdf.set_x(table_x)
    pdf.cell(col1_width, 10, "Centroid Coordinates", border=1, align="C")
    pdf.cell(col2_width, 10,
             f"({brain_info['centroid'][0]:.2f}, {brain_info['centroid'][1]:.2f}, {brain_info['centroid'][2]:.2f})", border=1, align="C")
    pdf.ln()
    pdf.set_x(table_x)
    pdf.cell(col1_width, 10, "Surface Area", border=1, align="C")
    pdf.cell(col2_width, 10,
             f"{brain_info['surface_area']:.2f} mm²", border=1, align="C")
    pdf.ln()

    pdf.add_page()
    pdf.set_font("Helvetica", 'B', 16)
    pdf.cell(0, 10, "Anatomical Localization & Clinical Analysis",
             new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
    pdf.ln(8)

    tumor_volume = calculate_tumor_volume(
        tumor_info['width'], tumor_info['height'], tumor_info['depth'])
    tumor_mass = estimate_tumor_mass(tumor_volume)
    analysis = get_anatomical_localization(tumor_info['centroid'])

    pdf.set_font("Helvetica", 'B', 12)
    pdf.cell(0, 8, f"Tumor Characteristics:",
             new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_font("Helvetica", size=12)
    pdf.multi_cell(0, 7, sanitize_text(
        f"- Estimated Mass: {tumor_mass:.2f} g\n"
        f"- Centroid MNI Coordinates: ({tumor_info['centroid'][0]:.1f}, "
        f"{tumor_info['centroid'][1]:.1f}, {tumor_info['centroid'][2]:.1f})"
    ))
    pdf.ln(5)

    pdf.set_font("Helvetica", 'B', 12)
    pdf.cell(0, 8, "Anatomical Localization:",
             new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_font("Helvetica", size=12)
    regions_str = ", ".join(
        analysis['regions']) if analysis['regions'] else "Unable to determine"
    pdf.multi_cell(0, 7, sanitize_text(
        f"Primary anatomical regions affected: {regions_str}"))
    pdf.ln(5)

    pdf.set_font("Helvetica", 'B', 12)
    pdf.cell(0, 8, "Clinical Implications:",
             new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_font("Helvetica", size=12)
    if analysis['implications']:
        for imp in analysis['implications']:
            pdf.cell(0, 7, f"- {imp}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    else:
        pdf.cell(0, 7, "No direct impact on eloquent brain areas",
                 new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(5)

    pdf.set_font("Helvetica", 'B', 12)
    pdf.cell(0, 8, f"Risk Assessment:", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_font("Helvetica", size=12)
    pdf.multi_cell(0, 7, sanitize_text(
        f"- Criticality: {analysis['critical_risk']}\n"
        "- Mass Effect: Present" if tumor_mass > 10 else "- Mass Effect: Minimal\n"
        "- Recommended: MRI spectroscopy + neurosurgical consultation"
    ))

    pdf_path = os.path.join(export_path, f"report_{file_id}.pdf")
    pdf.output(pdf_path)
    return pdf_path
