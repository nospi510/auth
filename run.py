from app import create_app

app = create_app()

if __name__ == '__main__':

    app.run(
        debug=True,
        host='0.0.0.0',
        port=5001,
        ssl_context=('certificats/ssl.crt', 'certificats/ssl.key')  # Active SSL avec le certificat et la clé
    )
