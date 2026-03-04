# Dataset de Evaluación Facial

Coloca aquí las imágenes organizadas **una carpeta por identidad (persona)**.

## Estructura esperada

```
eval_dataset/
  persona_A/
    001.jpg
    002.jpg
    003.jpg
  persona_B/
    001.jpg
    002.jpg
    003.jpg
  persona_C/
    001.jpg
    002.jpg
    003.jpg
```

## Requisitos mínimos

| Requisito       | Mínimo | Recomendado |
|-----------------|--------|-------------|
| Identidades     | 3      | 5           |
| Fotos por persona | 2    | 4–5         |
| Total imágenes  | 9      | 20–25       |

## División automática

El script `evaluate_with_mlflow.py` divide automáticamente:

- **Gallery (referencia / train):** las primeras `--n-gallery` imágenes de cada carpeta.
- **Queries (test):** el resto de imágenes.

Con `--n-gallery 1` (valor por defecto):
- 1 foto por persona → gallery (train)
- Resto de fotos → queries (test)

## Formatos soportados

`.jpg`, `.jpeg`, `.png`, `.bmp`, `.webp`

## Nota

Cada imagen debe contener **un rostro visible y bien iluminado**.
El detector YOLO interno rechaza imágenes donde no detecta rostro
(similitud coseno < 0.5) — esas imágenes se omiten con un aviso.

## Ejemplo de uso tras agregar imágenes

```powershell
uv run python training/evaluate_with_mlflow.py
```

```powershell
uv run python training/evaluate_with_mlflow.py `
  --data-dir training/eval_dataset `
  --n-gallery 1 `
  --n-steps 60 `
  --experiment face_recognition_eval `
  --run-name eval_v1
```

Ver resultados en MLflow UI:
```powershell
mlflow ui
# Abre http://127.0.0.1:5000
```
