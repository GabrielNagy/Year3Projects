from flask import Flask, render_template
import xmltodict
import json
app = Flask(__name__)


@app.route("/")
def template_test():
    with open('queue.xml') as fd:
        doc = xmltodict.parse(fd.read())
    doc = json.dumps(doc['queue']['link'])
    xml_json = json.loads(doc)
    return render_template('template.html', xml_json=xml_json)


if __name__ == '__main__':
    app.run(debug=True)
