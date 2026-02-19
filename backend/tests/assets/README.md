# assets/ — Recursos de prueba

Este directorio contiene los recursos estáticos utilizados por la suite de
pruebas del backend, principalmente imágenes para los tests del pipeline ML.

---

## face.jpg — Imagen de rostro para tests ML

Los tests en `ml/` y `api/test_acceso.py` requieren una imagen real con un
rostro humano para probar el pipeline completo de detección y extracción de
embeddings.

### Requisitos de la imagen

| Característica | Recomendación |
|---|---|
| Formato | JPEG o PNG |
| Resolución mínima | 200 × 200 px |
| Resolución recomendada | 400 × 400 px o más |
| Iluminación | Buena (sin sombras fuertes) |
| Posición del rostro | Frontal, centrado |
| Oclusión | Sin gafas de sol, sin mascarilla |
| Fondo | Preferiblemente uniforme |

> **Importante**: Solo coloca imágenes de personas que hayan dado su
> consentimiento explícito para ser usadas en entornos de prueba.

### Cómo agregar la imagen

1. Guarda tu imagen de prueba como:
   ```
   backend/tests/assets/face.jpg
   ```

2. Verifica que es detectada por los modelos:
   ```powershell
   uv run python -c "
   from backend.app.ml.face_model import get_embedding_from_bytes
   data = open('backend/tests/assets/face.jpg', 'rb').read()
   emb  = get_embedding_from_bytes(data)
   print('Embedding OK:', emb.shape if emb is not None else 'sin rostro detectado')
   "
   ```

3. Si el resultado es `sin rostro detectado`, prueba con una foto diferente
   (mejor iluminación, rostro más centrado, sin obstrucciones).

---

## Fuentes de imágenes libres de derechos

Se pueden usar imágenes de los siguientes repositorios de dominio público o
licencia Creative Commons para pruebas:

- **LFW (Labeled Faces in the Wild)**: http://vis-www.cs.umass.edu/lfw/
  Enfocado en reconocimiento facial, muchas fotos claras de personas reales.

- **UTKFace**: https://susanqq.github.io/UTKFace/
  Dataset público de rostros etiquetados por age/gender/ethnicity.

- **Flickr-Faces-HQ (FFHQ)**: https://github.com/NVlabs/ffhq-dataset
  Imágenes de alta calidad, licencia Creative Commons.

> Asegúrate de respetar la licencia de cada recurso antes de usarlo.

---

## Comportamiento sin face.jpg

Si `face.jpg` **no existe**, el fixture `face_image_bytes` en `conftest.py`:

1. Intenta descargar automáticamente una imagen desde Wikipedia Commons.
2. Si la descarga falla, genera una imagen sintética (forma ovalada con PIL).

La imagen sintética **no supera la detección facial** de YOLO/MTCNN, por lo
que los tests que requieren un rostro real se saltan automáticamente con
`pytest.skip(...)`. Esto no se considera un fallo.

---

## .gitignore

El archivo `face.jpg` está excluido del repositorio para respetar la privacidad.
Agrega esta línea a tu `.gitignore` si no lo está ya:

```gitignore
backend/tests/assets/face.jpg
backend/tests/assets/*.png
backend/tests/assets/*.jpeg
```
