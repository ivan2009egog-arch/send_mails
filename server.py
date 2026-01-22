import flask
import smtplib
import email.mime.text
import email.mime.multipart
import email.utils
import http


app = flask.Flask(__name__)


@app.route('/wake-up')
def hello_world():
    return 'Waking up'


@app.route('/send', methods=['POST', 'GET'])
def send_mail():
    if flask.request.method == 'GET':
        return 'Waking up'
    else:
        sender_email_raw = flask.request.form.get('sender_email')
        sender_password = flask.request.form.get('sender_password')
        recipient_email = flask.request.form.get('recipient_email')
        host = flask.request.form.get('host')
        port_raw = flask.request.form.get('port')
        subject = flask.request.form.get('subject')
        plain_email = flask.request.form.get('message')
        html_email = flask.request.form.get('html_message')

        required_fields = {
            'sender_email': sender_email_raw,
            'sender_password': sender_password,
            'recipient_email': recipient_email,
            'host': host,
            'port': port_raw,
            'subject': subject,
        }
        print(required_fields)
        missing = [name for name, value in required_fields.items() if not value]

        if missing:
            return (
                f'Not all required fields were given. Missing: {", ".join(missing)}',
                http.HTTPStatus.BAD_REQUEST
            )

        try:
            port = int(port_raw)
        except (ValueError, TypeError):
            return f'Invalid port: {port_raw}', http.HTTPStatus.BAD_REQUEST

        login_email = email.utils.parseaddr(sender_email_raw)[1]
        if not login_email:
            return 'Invalid sender_email', http.HTTPStatus.BAD_REQUEST

        message = email.mime.multipart.MIMEMultipart('alternative')
        message['Subject'] = subject
        message['From'] = sender_email_raw
        message['To'] = recipient_email

        if plain_email:
            message.attach(email.mime.text.MIMEText(plain_email, 'plain', 'utf-8'))
        if html_email:
            message.attach(email.mime.text.MIMEText(html_email, 'html', 'utf-8'))

        context = smtplib.ssl.create_default_context()
        try:
            if port == 587:
                with smtplib.SMTP(host, port) as server:
                    server.starttls(context=context)
                    server.login(login_email, sender_password)
                    server.sendmail(
                        login_email, recipient_email, message.as_string()
                    )
            elif port == 465:
                with smtplib.SMTP_SSL(host, port, context=context) as server:
                    server.login(login_email, sender_password)
                    server.sendmail(
                        login_email, recipient_email, message.as_string()
                    )
            else:
                return f'Unsupported port: {port}', http.HTTPStatus.BAD_REQUEST

        except Exception as e:
            return f'Error sending mail: {e}', http.HTTPStatus.INTERNAL_SERVER_ERROR
        return 'OK', http.HTTPStatus.OK


if __name__ == '__main__':
    app.run(debug=True)
