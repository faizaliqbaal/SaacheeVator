#!/usr/bin/env python3
"""
Downloads all required pretrained checkpoints for SadTalker and face enhancement.
"""
import os
import urllib.request
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
CHECKPOINTS_DIR = BASE_DIR / "SadTalker" / "checkpoints"
WEIGHTS_DIR = BASE_DIR / "SadTalker" / "gfpgan" / "weights"

HF_BASE_URL = "https://huggingface.co/vinthony/SadTalker/resolve/main/"
GH_BASE_URL = "https://github.com/OpenTalker/SadTalker/releases/download/v0.0.2-rc/"

CHECKPOINT_FILES = [
    (HF_BASE_URL + "auido2exp_00300-model.pth", CHECKPOINTS_DIR / "auido2exp_00300-model.pth"),
    (HF_BASE_URL + "auido2pose_00140-model.pth", CHECKPOINTS_DIR / "auido2pose_00140-model.pth"),
    (HF_BASE_URL + "epoch_20.pth", CHECKPOINTS_DIR / "epoch_20.pth"),
    (HF_BASE_URL + "facevid2vid_00189-model.pth.tar", CHECKPOINTS_DIR / "facevid2vid_00189-model.pth.tar"),
    (HF_BASE_URL + "mapping_00109-model.pth.tar", CHECKPOINTS_DIR / "mapping_00109-model.pth.tar"),
    (HF_BASE_URL + "mapping_00229-model.pth.tar", CHECKPOINTS_DIR / "mapping_00229-model.pth.tar"),
    (HF_BASE_URL + "shape_predictor_68_face_landmarks.dat", CHECKPOINTS_DIR / "shape_predictor_68_face_landmarks.dat"),
    (HF_BASE_URL + "wav2lip.pth", CHECKPOINTS_DIR / "wav2lip.pth"),
    (GH_BASE_URL + "SadTalker_V0.0.2_256.safetensors", CHECKPOINTS_DIR / "SadTalker_V0.0.2_256.safetensors"),
    (GH_BASE_URL + "SadTalker_V0.0.2_512.safetensors", CHECKPOINTS_DIR / "SadTalker_V0.0.2_512.safetensors"),
    (HF_BASE_URL + "BFM_Fitting/01_MorphableModel.mat", CHECKPOINTS_DIR / "BFM_Fitting" / "01_MorphableModel.mat"),
    (HF_BASE_URL + "BFM_Fitting/BFM09_model_info.mat", CHECKPOINTS_DIR / "BFM_Fitting" / "BFM09_model_info.mat"),
    (HF_BASE_URL + "BFM_Fitting/BFM_exp_idx.mat", CHECKPOINTS_DIR / "BFM_Fitting" / "BFM_exp_idx.mat"),
    (HF_BASE_URL + "BFM_Fitting/BFM_front_idx.mat", CHECKPOINTS_DIR / "BFM_Fitting" / "BFM_front_idx.mat"),
    (HF_BASE_URL + "BFM_Fitting/Exp_Pca.bin", CHECKPOINTS_DIR / "BFM_Fitting" / "Exp_Pca.bin"),
    (HF_BASE_URL + "BFM_Fitting/facemodel_info.mat", CHECKPOINTS_DIR / "BFM_Fitting" / "facemodel_info.mat"),
    (HF_BASE_URL + "BFM_Fitting/select_vertex_id.mat", CHECKPOINTS_DIR / "BFM_Fitting" / "select_vertex_id.mat"),
    ("https://github.com/xinntao/facexlib/releases/download/v0.1.0/detection_Resnet50_Final.pth", WEIGHTS_DIR / "detection_Resnet50_Final.pth"),
    ("https://github.com/xinntao/facexlib/releases/download/v0.1.0/alignment_WFLW_4HG.pth", WEIGHTS_DIR / "alignment_WFLW_4HG.pth")
]

def download_models():
    CHECKPOINTS_DIR.mkdir(parents=True, exist_ok=True)
    WEIGHTS_DIR.mkdir(parents=True, exist_ok=True)
    print("▶ Verifying model checkpoints...")
    for url, dest in CHECKPOINT_FILES:
        dest.parent.mkdir(parents=True, exist_ok=True)
        if dest.exists() and dest.stat().st_size > 1000:
            print(f"✔ Already present: {dest.name} ({dest.stat().st_size // (1024*1024)} MB)")
            continue
        print(f"⬇ Downloading {dest.name}...")
        urllib.request.urlretrieve(url, dest)
        print(f"✔ Saved: {dest.name}")
    print("\n🎉 All checkpoints verified and ready!")

if __name__ == "__main__":
    download_models()
