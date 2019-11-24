from flask import Flask

app = Flask(__name__)

@app.route("/serve-image/<path:image_id>")
def serve_image(image_id):
    return app.send_static_file('%s.svg'%image_id)

if __name__ == "__main__":
  app.run()
