# main.py
from flask import Flask, request, jsonify
import subprocess
import json

app = Flask(__name__)

@app.route('/consultar', methods=['GET'])
def consultar_nif():
    nif = request.args.get('nif')
    if not nif:
        return jsonify({"status": "erro", "mensagem": "NIF não fornecido"}), 400

    try:
        # Chama o script Python passando o NIF como argumento
        result = subprocess.run(
            ['python3', 'consultar_nif.py', nif],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        if result.returncode != 0:
            return jsonify({"status": "erro", "mensagem": "Erro ao executar o script"}), 500

        return jsonify(json.loads(result.stdout))
    except Exception as e:
        return jsonify({"status": "erro", "mensagem": str(e)}), 500
