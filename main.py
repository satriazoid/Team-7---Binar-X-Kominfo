from flask import Flask, jsonify, render_template, request
from flasgger import Swagger, LazyString, LazyJSONEncoder
from flasgger import swag_from
import tensorflow as tf
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.text import tokenizer_from_json
from tensorflow.keras.preprocessing.sequence import pad_sequences
import pandas as pd
import sqlite3

# Load the neural network and LSTM model function
from api import neural_network_predict, lstm_predict

app = Flask(__name__)
app.json_encoder = LazyJSONEncoder

swagger_template = dict(
    info = {
        'title': LazyString(lambda:'API Documentation for Data Processing and Modeling'),
        'version': LazyString(lambda:'1.0.0'),
        'description': LazyString(lambda:'Dokumentasi API untuk Data Processing dan Modeling')
        }, host = LazyString(lambda: request.host)
    )

swagger_config = {
        "headers":[],
        "specs":[
            {
            "endpoint":'docs',
            "route":'/docs.json'
            }
        ],
        "static_url_path":"/flasgger_static",
        "swagger_ui":True,
        "specs_route":"/docs/"
    }

swagger = Swagger(app, template=swagger_template, config=swagger_config)
###############################################################################################################

def db_connection():
    # Connecting to database
    conn = sqlite3.connect('sql.db', check_same_thread=False)
    c = conn.cursor()
    # Defining and executing the query for table data if it not available
    conn.execute('''CREATE TABLE IF NOT EXISTS sentiment_analysis_library (id INTEGER PRIMARY KEY AUTOINCREMENT, text varchar(255), sentiment varchar(255), tipe varchar(255));''')
    #conn.execute('create table if not exists input_data (input_text varchar(255), output_text varchar(255))')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def home():
    conn = db_connection()
    posts = conn.execute('SELECT * FROM sentiment_analysis_library').fetchall()
    conn.close()
    return render_template("index.html", posts=posts)

@swag_from("docs/delete_all.yml", methods=['GET'])
@app.route('/delete_all', methods=['GET'])
def delete_all():
    conn = db_connection()
    conn.execute('''DELETE FROM sentiment_analysis_library;''')
    conn.commit()
    conn.close()
    json_response = {
        'status_code': 200,
        'description': "Delete process is success",
        'data': "Delete all",
    }

    return jsonify(json_response)

@swag_from("docs/get.yml", methods = ['GET'])
@app.route('/get_all', methods = ['GET'])
def get_all():
    conn = db_connection()
    sql_query = pd.read_sql_query ('''
                               SELECT
                               *
                               FROM sentiment_analysis_library
                               ''', conn)
    conn.close()
    df = pd.DataFrame(sql_query, columns = ['id','text', 'sentiment', 'tipe'])
    df = df.to_dict('records')

    response_data = jsonify(df)
    return response_data

@swag_from("docs/post_neural_network.yml", methods=['POST'])
@app.route('/post_neural_network', methods=['POST'])
def manual_input_neural_network():
    # input_json = request.get_json(force=True)
    # text = input_json['text']
    # sentiment = neural_network_predict(text)

    conn = db_connection()
    input_txt = request.form.get("manual_input_neural_network")
    output_txt = neural_network_predict(str(input_txt))
    
    
    query_txt = 'insert into input_data (input_text , output_text) values (?,?)'
    val = (input_txt,output_txt)
    conn.execute(query_txt,val)
    conn.commit()

    return_txt = { "input" :input_txt, "output" : output_txt}

    return jsonify (return_txt)
    conn.close()

@swag_from('docs/upload_neural_network.yml', methods=['POST'])
@app.route('/upload_neural_network', methods=['POST'])
def upload_neural_network():
    conn = db_connection()
    file = request.files['file']
    try:
        data = pd.read_csv(file, encoding='iso-8859-1', error_bad_lines=False)
    except:
        data = pd.read_csv(file, encoding='utf-8', error_bad_lines=False)

    results = []

    for text in data['text']:
        sentiment = neural_network_predict(text)

        # Insert the text and sentiment into the database
        conn.execute("INSERT INTO sentiment_analysis_library (text, sentiment, tipe) VALUES (?, ?, ?)", (text, sentiment, 'NN'))
        conn.commit()

        result = {
            'text': text,
            'sentiment': sentiment
        }

        results.append(result)
    conn.close()

    return jsonify(results)

@swag_from("docs/post_lstm.yml", methods=['POST'])
@app.route('/post_lstm', methods=['POST'])
def manual_input_lstm():

    conn = db_connection()
    input_txt = request.form.get("post_lstm")
    output_txt = lstm_predict(str(input_txt))
    
    #conn.execute('create table if not exists input_data (input_text varchar(255), output_text varchar(255))')
    query_txt = 'insert into input_data (input_text , output_text) values (?,?)'
    val = (input_txt,output_txt)
    conn.execute(query_txt,val)
    conn.commit()
    conn.close()
    
    return_txt = { "input" :input_txt, "output" : output_txt}
    
    return jsonify (return_txt)
    


    # conn = db_connection()
    # input_json = request.get_json(force=True)
    # text = input_json['text']
    # sentiment = lstm_predict(text)

    # # Insert the text and sentiment into the database
    # conn.execute("INSERT INTO sentiment_analysis_library (text, sentiment, tipe) VALUES (?, ?, ?)", (text, sentiment, 'LSTM'))
    # conn.commit()
    # conn.close()

    # result = {
    #     'text': text,
    #     'sentiment': sentiment
    # }

    # return jsonify(result)

@swag_from('docs/upload_lstm.yml', methods=['POST'])
@app.route('/upload_lstm', methods=['POST'])
def upload_lstm():
    conn = db_connection()
    file = request.files['file']
    try:
        data = pd.read_csv(file, encoding='iso-8859-1', error_bad_lines=False)
    except:
        data = pd.read_csv(file, encoding='utf-8', error_bad_lines=False)

    results = []

    for text in data['text']:
        sentiment = lstm_predict(text)

        # Insert the text and sentiment into the database
        conn.execute("INSERT INTO sentiment_analysis_library (text, sentiment, tipe) VALUES (?, ?, ?)", (text, sentiment, 'LSTM'))
        conn.commit()

        result = {
            'text': text,
            'sentiment': sentiment
        }

        results.append(result)
    conn.close()

    return jsonify(results)

if __name__ == '__main__':
    app.run()

