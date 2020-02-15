from forumapp import db, app

if __name__ == '__main__':
    db.create_all()
    app.run(host='0.0.0.0', port=80)

