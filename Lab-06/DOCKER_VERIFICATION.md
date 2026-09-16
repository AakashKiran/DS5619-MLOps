# Docker verification

Fill this in after you build and run your container (see README.md,
"Part 2 — Dockerfile"). This is how we confirm your container actually works, since an
automated grader running in a sandbox may not always have Docker-in-Docker
available.

## Build

Paste the command you ran and its final output line (the one showing the
built image ID/tag):

```bash
$ docker build -t week6-detector .

 => => naming to docker.io/library/week6-detector:latest                                                                                               0.0s
```
- The Docker build output showed the image tag but did not display the Docker IMAGE ID directly, so I ran docker images week6-detector to obtain it.
```bash
$ docker images week6-detector

IMAGE                   ID             DISK USAGE   CONTENT SIZE   EXTRA
week6-detector:latest   5610d4ed77fe        233MB         57.4MB
```

## Run

Paste the command you used to start the container (should map a host port
to the container's 8080):

```bash
$ docker run --rm -p 8080:8080 week6-detector

 * Serving Flask app 'app'
 * Debug mode: off
WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.
 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:8080
 * Running on http://172.17.0.2:8080
Press CTRL+C to quit
```

## Verify

Paste the exact `curl` commands and their JSON output for both endpoints,
run against the running container (not against `python src/app.py` directly
— the point is to prove the *container* works):

```bash
$ curl http://localhost:8080/health

{"status":"ok"}
```
```bash
$ curl -F "image=@data/fixtures/camera_A_daylight/000.jpg" http://localhost:8080/detect

{"count":4,"detections":[{"bbox":[80,5,21,6],"category_id":0,"id":0,"image_id":0,"score":0.951},{"bbox":[264,20,20,26],"category_id":2,"id":1,"image_id":0,"score":0.98},{"bbox":[84,36,23,27],"category_id":5,"id":2,"image_id":0,"score":0.98},{"bbox":[27,117,37,22],"category_id":2,"id":3,"image_id":0,"score":0.98}]}
```
