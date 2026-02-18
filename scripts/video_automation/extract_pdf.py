import fitz  # PyMuPDF
import os
import json

import shutil

def extract_from_pdf(pdf_path, output_dir):
    # Limpar diretório de saída para evitar arquivos antigos
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    
    os.makedirs(output_dir, exist_ok=True)
    assets_dir = os.path.join(output_dir, "assets")
    os.makedirs(assets_dir, exist_ok=True)
    
    doc = fitz.open(pdf_path)
    scenes = []
    
    # Adicionar CTA Inicial
    scenes.append({
        "text": "Se inscreva no canal AlêAtório para não perder nenhum vídeo!",
        "image": "cta_start.jpg" # Precisaremos gerar ou usar a primeira imagem
    })
    
    for i, page in enumerate(doc):
        text = page.get_text().strip()
        
        # Renderizar a página como imagem (pixmap) para garantir que pegamos tudo
        img_filename = f"scene_{i+1:03d}.jpg"
        pix = page.get_pixmap(matrix=fitz.Matrix(2, 2)) # 2x zoom
        pix.save(os.path.join(assets_dir, img_filename))
            
        scenes.append({
            "text": text if text else f"Cena {i+1}",
            "image": img_filename
        })
    
    # Mapear primeira e última imagem para CTAs
    first_img = scenes[1]["image"] if len(scenes) > 1 else "scene_001.jpg"
    last_img = scenes[-1]["image"] if len(scenes) > 1 else "scene_001.jpg"
    
    scenes[0]["image"] = first_img
    
    # Adicionar CTA Final
    scenes.append({
        "text": "Se você gostou, deixe seu like, se inscreva no canal AlêAtório e ative o sininho! Até o próximo vídeo.",
        "image": last_img
    })
    
    # Salvar scenes.json
    with open(os.path.join(output_dir, "scenes.json"), "w", encoding="utf-8") as f:
        json.dump({"scenes": scenes}, f, ensure_ascii=False, indent=4)
    
    print(f"✅ Extração concluída: {len(scenes)} cenas processadas.")

if __name__ == "__main__":
    pdf = r"C:\Users\alexa\Desktop\Video teste\O Banquete de Cinzas.pdf"
    output = "output"
    extract_from_pdf(pdf, output)
