# NOTES.md — Week 6: Containerize and Serve a Detector

**Student ID used with `generate_for_student.py`:**
<!-- paste the --student-id value you used -->
- Student ID: 142301002
- Seed: 4228078734

## Built image size

<!-- What image size did `docker images` report for week6-detector? -->

```bash
$ docker images week6-detector

IMAGE                   ID             DISK USAGE   CONTENT SIZE   EXTRA
week6-detector:latest   5610d4ed77fe        233MB         57.4MB
```
The image reported 233MB disk usage and 57.4MB content size.


## Swapping in a real checkpoint

<!-- What's the single biggest thing you'd change about this Dockerfile if
     src/mock_detector.py were swapped for a real torch-based checkpoint?
     (Think about what that does to build time and image size.) -->

- If src/mock_detector.py were replaced with a real Torch-based checkpoint, I would change the base image to be one that is compatible with PyTorch and other packages required for torch runtime. This also requires including PyTorch and other required dependencies in requirements.txt
- This would significantly increase the image size and build time compared with the current lightweight python:3.13-slim image.

## My Approach

Initially I completed the instructions mentioned in the set-up in README.md. This involved creating virtual environment, installing the required dependencies inside it and creation of custom dataset (CCTV images). Then I filled the missing parts of below functions in src/app.py:
- load_image_from_upload(file_storage) - Here file_storage.read() returns raw bytes of the image. It was transformed to python readable file-format using io.BytesIO. Then the image was opened and converted to RGB colour theme. This was then returned by the function
- run_detection(image) - This function first creates a list of Detection objects ([Detection(...), Detection(...), Detection(...)]). Then a dictionary containing the count of detection objects and this list itself is returned
- /detect route in create_app() - It first handles the case where image is absent by raising status 400. Otherwise, it calls the 2 functions defined above and returns a json object of dictionary returned by run_detection function and status 200.

```python src/app.py``` was run and output was as expected. Once all 4 test cases were passed upon running ```pytest tests/ -q```, I moved to container based approach. This involved filling the Dockerfile
- The base image used is python:3.13-slim which is a minimal python image that excludes any unnecessary packages. This suffices since we are not working with heavy python libraries like PyTorch
- It then creates a folder named 'app' and sets it as the root directory
- It copies over the requirements.txt to this root directory
- The packages in requirements.txt is installed in the python environment in the image. no chache flag ensures no downloaded package is cached, further minimizing the overall storage space required
- Later the files in src folder in working directory is copied to a new folder created inside app directory (also named src)
- This container expects to receive traffic on port 8080
- Finally, CMD instructs the container to launch the Flask server by executing python3 src/app.py