from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_mysqldb import MySQL

app = Flask(__name__)

app.secret_key = b'"\xedP\'\x13\xe6\xad\x84t\x10\xafi0l\xee\x83'
app.config.from_object(__name__)

app.secret_key = "flash message"

#CONFIGURACIONES DE MYSQL
app.config['MYSQL_HOST'] = 'us-cdbr-east-03.cleardb.com'
app.config['MYSQL_USER'] = 'bef79789702297'
app.config['MYSQL_PASSWORD'] = '1e78f586'
app.config['MYSQL_DB'] = 'heroku_a718be810d404c7'
app.config['OPTIONS'] = {'ssl': {'ca':'/path/to/ca-cert.pem', 'cert':'/path/to/cert.pem', 'key':'/path/to/key.pem'},}


mysql = MySQL(app)

#ENRUTAMIENTO
@app.route('/', methods = ['POST', 'GET'])
def Login():
    if request.method == "GET":
        if 'usuario' in session:
            return redirect(url_for('Index'))
        else:
            return render_template('login.html')

    elif request.method == "POST":
        usuario = request.form['usuario']
        password = request.form['password']

        cur = mysql.connection.cursor()
        cur.execute(F"CALL sp_login(\"{usuario}\",\"{password}\")")
        data = cur.fetchall()
        cur.close()
        if len(data) == 1 :
            session['usuario'] = usuario
            session['id_usuario'] = data[0][0]
            return redirect(url_for('Index'))
        else:
            flash("Datos incorrectos")
            return redirect(url_for('Login'))


@app.route('/logout', methods = ['POST'])
def Logout():
    if request.method == "POST":
        session.pop('usuario', None)
        session.pop('id_usuario', None)
        return redirect(url_for('Login'))


@app.route('/registrar', methods = ['POST', 'GET'])
def Registrar():
    if request.method == "GET":
        if 'usuario' in session:
            return redirect(url_for('Index'))
        else:
            return render_template('registrar.html')
    elif request.method == "POST":
        try:
            usuario = request.form['usuario']
            password = request.form['password']

            cur = mysql.connection.cursor()
            cur.execute(F"CALL sp_agregaUsuarios(\"{usuario}\",\"{password}\")")
            cur.close()
            mysql.connection.commit()
            flash("Registrado con éxito")
            return redirect(url_for('Registrar'))
        except:
            flash("Error")
            return redirect(url_for('Registrar'))


@app.route('/inventario', methods = ['POST', 'GET'])
def Index():
    if 'usuario' not in session:
        return redirect(url_for('Login'))
    id = session['id_usuario']

    cur = mysql.connection.cursor()
    cur.execute(F"CALL sp_consultaProductos({id})")
    productos = cur.fetchall()
    cur.close()

    cur = mysql.connection.cursor()
    cur.execute(F"CALL sp_consultaVentas({id})")
    ventas = cur.fetchall()
    cur.close()

    cur = mysql.connection.cursor()
    cur.execute(F"CALL sp_consultaVentasMensual({id})")
    total = cur.fetchall()
    cur.close()

    return render_template('index.html', productos = productos, ventas = ventas, total = total)


@app.route('/insert', methods = ['POST'])
def insert():
    if 'usuario' not in session:
        return redirect(url_for('Login'))
    id = session['id_usuario']

    if request.method == "POST":
        try:
            flash("Se agregó correctamente")

            nombre = request.form['nombre']
            cantidad = request.form['cantidad']
            precio = request.form['precio']
            caducidad = request.form['caducidad']
            categoria = request.form['categoria']

            cur = mysql.connection.cursor()
            cur.execute(F"CALL sp_agregaProductos(\"{nombre}\", {cantidad}, {precio}, \"{caducidad}\", \"{categoria}\", {id});")
            cur.close()
            mysql.connection.commit()
            return redirect(url_for('Index'))
        except:
            flash("No se puede agregar boleta o CURP existentes")
            return redirect(url_for('Index'))


@app.route('/update', methods = ['POST'])
def update():
    if 'usuario' not in session:
        return redirect(url_for('Login'))
    id = session['id_usuario']

    if request.method == 'POST':
        try:
            flash("Se actualizó correctamente")
            #id_data = request.form['id']
            nombre = request.form['nombre']
            cantidad = request.form['cantidad']
            precio = request.form['precio']
            caducidad = request.form['caducidad']
            categoria = request.form['categoria']

            cur = mysql.connection.cursor()
            cur.execute(F"CALL sp_actualizaProducto(\"{nombre}\", {cantidad}, {precio}, \"{caducidad}\", \"{categoria}\", {id});")
            cur.close()
            mysql.connection.commit()
            return redirect(url_for('Index'))
        except:
            flash("No se puede actualizar")
            return redirect(url_for('Index'))


@app.route('/delete', methods = ['POST'])
def delete():
    if request.method == 'POST':
        
        nombre = request.form['nombre']

        cur = mysql.connection.cursor()
        cur.execute(F"CALL sp_borraProducto(1, \"{nombre}\")")
        cur.close()
        mysql.connection.commit()
        return redirect(url_for('Index'))


@app.route('/venta', methods = ['POST'])
def venta():
    if request.method == 'POST':
        
        id_data = request.form['id']
        cantidad = request.form['cantidad']

        cur = mysql.connection.cursor()
        cur.execute(F"CALL sp_generarVenta({id_data}, {cantidad})")
        cur.close()
        mysql.connection.commit()
        return redirect(url_for('Index'))



if __name__ == "__main__":
    app.run(debug = True)