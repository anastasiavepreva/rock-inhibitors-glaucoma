# Custom impelementaion of EvoSBDD framework.

Dependencies:
- joblib
- rdkit
- numpy
- torch
- cma
- unidock
- unidock_tools
- mflow

Run:
```
python main.py \
    --center_x 26.909 \
    --center_y 47.024 \
    --center_z 52.508 \
    --receptor "./6ed6_rec.pdbqt" \
    --corneal_model "./corneal.pkl" \
    --melanin_model "./melanin.pkl" \
    --irritation_model "./irritation.pkl" \
    --moflow_model "./moflow/results/zinc250k_512t2cnn_256gnn_512-64lin_10flow_19fold_convlu2_38af-1-1mask"
```