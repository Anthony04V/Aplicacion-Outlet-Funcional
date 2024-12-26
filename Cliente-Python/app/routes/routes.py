from app import app
from datetime import datetime
from instance.config import DATABASE_CONFIG
from flask import render_template, request, redirect, url_for, flash, session
from app.models.http_service import POST_Service, GET_Service, AdministradorService, DeleteService, PUT_Service
import pyodbc

# Instanciar los servicios
GET_Services = GET_Service(base_url="https://localhost:7005/api/Controllers") #API GET
POST_Services = POST_Service(base_url="https://localhost:7085/api/Controllers") #API POST
admin_service = AdministradorService(base_url="https://localhost:7005/api/Controllers") #API POST PERO PARA ADMI N
delete_service = DeleteService(base_url="https://localhost:7000/api/Controllers") #API DELETE
PUT_Services = PUT_Service(base_url="https://localhost:7002/api/Controllers") #API PUT


##EXTRAS##

@app.template_filter('format_currency')
def format_currency(value):
    return f"{value:,.2f}"  # Separadores de miles y dos decimales

##########



# Crear la función para conectarse a SQL Server
def get_db_connection():
    conn_str = (
        f"DRIVER={{{DATABASE_CONFIG['driver']}}};"
        f"SERVER={DATABASE_CONFIG['server']};"
        f"DATABASE={DATABASE_CONFIG['database']};"
        f"Trusted_Connection={DATABASE_CONFIG['trusted_connection']};"
    )
    return pyodbc.connect(conn_str)


@app.route('/')
def index():
    rol = session.get('rol', None)  # Obtener el rol de la sesión
    if rol == 'admin':
        return redirect(url_for('dashboard_admin'))  # Redirigir al panel de admin
    elif rol == 'cliente':
        return redirect(url_for('tienda'))  # Vista del cliente
    else:
        return redirect(url_for('login'))  # Si no está autenticado





@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario = request.form['usuario']
        contrasena = request.form['password']

        # Obtener usuario desde la base de datos
        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            query = "SELECT Contrasena, Rol FROM Usuarios WHERE Usuario = ?"
            cursor.execute(query, (usuario,))
            result = cursor.fetchone()

            if result and result[0] == contrasena:
                flash('Inicio de sesión exitoso', 'success')
                session['usuario'] = usuario
                session['rol'] = result[1]  # Guardar el rol en la sesión

                if session['rol'] == 'admin':
                    return redirect(url_for('dashboard_admin'))  # Redirigir al panel de admin
                elif session['rol'] == 'cliente':
                    return redirect(url_for('tienda'))  # Redirigir al panel de cliente
            else:
                flash('Usuario o contraseña incorrectos', 'danger')
        except Exception as e:
            flash(f"Error al autenticar: {str(e)}", 'danger')
        finally:
            conn.close()

    return render_template('login.html')


@app.route('/dashboard_admin', methods=['GET'])
def dashboard_admin(): 
    if 'rol' in session and session['rol'] == 'admin':
        return render_template('dashboard_admin.html', usuario=session['usuario'])
    else:
        flash("No tienes permisos para acceder a esta pagina. ", "danger")   
        return render_template('login')


@app.route('/logout')
def logout():
    # Limpiar toda la sesión
    session.clear()
    flash('Sesión cerrada correctamente', 'success')
    return redirect(url_for('login'))

#LOGICA PARA PRODUCTOS GET, PUT, POST
@app.route('/producto/create', methods=['GET', 'POST'])
def create_producto():
    categorias = []
    productos = []
    try:
        categorias = GET_Services.get_categorias()
        productos = GET_Services.get_productos()  # Obtener productos existentes
    except Exception as e:
        flash(f'Error al cargar datos: {str(e)}', 'danger')

    if request.method == 'POST':
        nombre = request.form['nombre']
        precio = float(request.form['precio'])
        cantidad_en_stock = int(request.form['cantidad_en_stock'])
        id_categoria = int(request.form['id_categoria'])

        # Validar nombre único
        if any(producto['nombreProducto'].lower() == nombre.lower() for producto in productos):
            flash('El nombre del producto ya existe. Por favor, elija otro nombre.', 'danger')
            return render_template('create_producto.html', categorias=categorias, productos=productos)

        data = {
            "nombreProducto": nombre,
            "precio": precio,
            "cantidadEnStock": cantidad_en_stock,
            "producto_Update": "string",
            "idCategoria": id_categoria
        }

        try:
            POST_Services.create_producto(data)
            flash('Producto creado con éxito', 'success')
            return redirect(url_for('create_producto'))
        except Exception as e:
            flash(f'Error al crear el producto: {str(e)}', 'danger')

    return render_template('create_producto.html', categorias=categorias, productos=productos)


@app.route('/producto/update/<int:id>', methods=['GET', 'POST'])
def update_producto(id):
    producto = {}
    categorias = []
    if request.method == 'GET':
        try:
            productos = GET_Services.get_productos()
            categorias = GET_Services.get_categorias()
            producto = next((p for p in productos if p['idProducto'] == id), None)
            if not producto:
                flash('Producto no encontrado.', 'danger')
                return redirect(url_for('create_producto'))
        except Exception as e:
            flash(f"Error al cargar datos: {e}", "danger")

    if request.method == 'POST':
        nombre = request.form['nombre']
        precio = float(request.form['precio'])
        cantidad_en_stock = int(request.form['cantidad_en_stock'])
        id_categoria = int(request.form['id_categoria'])
        data = {
            "idProducto": id,
            "nombreProducto": nombre,
            "precio": precio,
            "cantidadEnStock": cantidad_en_stock,
            "producto_Update": "string",  # Temporal, será asignado por el backend
            "idCategoria": id_categoria
        }

        try:
            response = PUT_Services.update_producto(id, data)
            # Manejo de respuesta
            if isinstance(response, dict) and "message" in response:
                flash(response["message"], "success")
            else:
                flash("Producto actualizado con éxito", "success")
            return redirect(url_for('create_producto'))
        except request.exceptions.JSONDecodeError:
            # Manejar respuesta vacía
            flash("Producto actualizado correctamente, pero no se recibió respuesta del servidor.", "warning")
            return redirect(url_for('create_producto'))
        except Exception as e:
            flash(f"Error al actualizar el producto: {e}", "danger")

    return render_template('update_producto.html', producto=producto, categorias=categorias)

@app.route('/producto/delete/<int:id>', methods=['POST'])
def delete_producto(id):
    try:
        delete_service.delete_producto(id)
        flash('Producto eliminado correctamente', 'success')
    except ValueError as e:
        flash(str(e), 'danger')
    except Exception as e:
        flash(f'Error al eliminar el producto: {str(e)}', 'danger')
    return redirect(url_for('create_producto'))

#LOGICA PARA CATEGORIAS GET, PUT, POST
@app.route('/categoria/create', methods=['GET', 'POST'])
def create_categoria():
    categorias = []
    try:
        categorias = GET_Services.get_categorias()  # Obtener categorías existentes
    except Exception as e:
        flash(f'Error al cargar categorías: {str(e)}', 'danger')

    if request.method == 'POST':
        nombre = request.form['nombre']

        # Validar nombre único
        if any(categoria['nombreCategoria'].lower() == nombre.lower() for categoria in categorias):
            flash('El nombre de la categoría ya existe. Por favor, elija otro nombre.', 'danger')
            return render_template('create_categoria.html', categorias=categorias)

        data = {
            "nombreCategoria": nombre,
            "categoria_Update": "string"
        }

        try:
            POST_Services.create_categoria(data)
            flash('Categoría creada con éxito', 'success')
            return redirect(url_for('create_categoria'))
        except Exception as e:
            flash(f'Error al crear la categoría: {str(e)}', 'danger')

    return render_template('create_categoria.html', categorias=categorias)


#LOGICA DE CATEGORIA PUT, DELETE

@app.route('/categoria/update/<int:id>', methods=['GET', 'POST'])
def update_categoria(id):
    categoria = {}
    if request.method == 'GET':
        try:
            categorias = GET_Services.get_categorias()
            categoria = next((c for c in categorias if c['idCategoria'] == id), None)
            if not categoria:
                flash('Categoría no encontrada.', 'danger')
                return redirect(url_for('create_categoria'))
        except Exception as e:
            flash(f"Error al cargar la categoría: {e}", "danger")

    if request.method == 'POST':
        nombre = request.form['nombre']
        data = {
            "idCategoria": id,
            "nombreCategoria": nombre,
            "categoria_Update": "string"  # Temporal, será asignado por el backend
        }

        try:
            PUT_Services.update_categoria(id, data)
            flash("Categoría actualizada con éxito", "success")
            return redirect(url_for('create_categoria'))
        except Exception as e:
            flash(f"Error al actualizar la categoría: {e}", "danger")

    return render_template('update_categoria.html', categoria=categoria)


@app.route('/categoria/delete/<int:id>', methods=['POST'])
def delete_categoria(id):
    try:
        delete_service.delete_categoria(id)
        flash('Categoría eliminada correctamente', 'success')
    except ValueError as e:
        flash(str(e), 'danger')
    except Exception as e:
        flash(f'Error al eliminar la categoría: {str(e)}', 'danger')
    return redirect(url_for('create_categoria'))



### OPCIONES PARA CLIENTE 

@app.route('/tienda', methods=['GET', 'POST'])
def tienda():
    productos = []
    categorias = []
    filtro_categoria = request.args.get('categoria', None)  # Filtro por categoría (GET param)

    try:
        categorias = GET_Services.get_categorias()  # Obtener categorías
        productos = GET_Services.get_productos()  # Obtener productos

        # Filtrar productos si se selecciona una categoría
        if filtro_categoria:
            productos = [p for p in productos if p['idCategoria'] == int(filtro_categoria)]
    except Exception as e:
        flash(f"Error al cargar los productos: {e}", "danger")

    return render_template('tienda.html', productos=productos, categorias=categorias, filtro_categoria=filtro_categoria)


@app.route('/carrito/agregar/<int:id>', methods=['POST'])
def agregar_al_carrito(id):
    cantidad = int(request.form['cantidad'])
    try:
        productos = GET_Services.get_productos()
        producto = next((p for p in productos if p['idProducto'] == id), None)
        if not producto:
            flash("Producto no encontrado", "danger")
            return redirect(url_for('tienda'))
        
        # Obtener el carrito actual
        carrito = session.get('carrito', [])
        
        # Verificar si el producto ya está en el carrito
        producto_existente = next((item for item in carrito if item['idProducto'] == id), None)
        if producto_existente:
            producto_existente['cantidad'] += cantidad
        else:
            # Agregar el producto al carrito
            carrito.append({
                'idProducto': producto['idProducto'],
                'nombreProducto': producto['nombreProducto'],
                'precio': producto['precio'],
                'cantidad': cantidad
            })

        session['carrito'] = carrito
        flash("Producto agregado al carrito", "success")
    except Exception as e:
        flash(f"Error al agregar al carrito: {e}", "danger")

    return redirect(url_for('tienda'))


@app.route('/carrito', methods=['GET'])
def ver_carrito():
    carrito = session.get('carrito', [])
    total = sum(item['precio'] * item['cantidad'] for item in carrito)

    return render_template('carrito.html', carrito=carrito, total=total)


#CARRITO DE LA COMPRA 


@app.route('/carrito/comprar', methods=['POST'])
def confirmar_compra():
    try:
        carrito = session.get('carrito', [])
        if not carrito:
            flash('El carrito está vacío', 'danger')
            return redirect(url_for('ver_carrito'))

        total = sum(item['precio'] * item['cantidad'] for item in carrito)

        conn = get_db_connection()
        cursor = conn.cursor()

        # Insertar la venta
        cursor.execute("INSERT INTO Ventas (Total, FechaVenta) OUTPUT INSERTED.IdVenta VALUES (?, GETDATE())", (total,))
        id_venta = cursor.fetchone()[0]

        # Insertar el detalle de la venta y actualizar el stock
        for item in carrito:
            # Insertar el detalle
            cursor.execute(
                "INSERT INTO DetalleVenta (IdVenta, IdProducto, Cantidad, Precio) VALUES (?, ?, ?, ?)",
                (id_venta, item['idProducto'], item['cantidad'], item['precio'])
            )

            # Actualizar el stock del producto
            cursor.execute(
                "UPDATE Productos SET CantidadEnStock = CantidadEnStock - ? WHERE IdProducto = ?",
                (item['cantidad'], item['idProducto'])
            )

        conn.commit()
        conn.close()

        # Vaciar el carrito
        session.pop('carrito', None)
        flash('Compra realizada con éxito', 'success')
    except Exception as e:
        flash(f"Error al confirmar la compra: {e}", "danger")
    return redirect(url_for('tienda'))

#ELIMINAR ARTICULOS

@app.route('/carrito/eliminar/<int:id>', methods=['POST'])
def eliminar_del_carrito(id):
    try:
        carrito = session.get('carrito', [])
        nuevo_carrito = [item for item in carrito if item['idProducto'] != id]
        session['carrito'] = nuevo_carrito
        flash('Producto eliminado del carrito', 'success')
    except Exception as e:
        flash(f"Error al eliminar el producto del carrito: {e}", 'danger')
    return redirect(url_for('ver_carrito'))


### VENTAS ###
@app.route('/venta/detalle/<int:id>', methods=['GET'])
def detalle_venta(id):
    try:
        detalle = GET_Services.get_detalle_venta(id)  # Llama al servicio que obtiene el detalle
        if not detalle:
            flash('No se encontraron detalles para esta venta.', 'danger')
            return redirect(url_for('ventas'))

        # Verifica qué datos estás pasando
        print(f"Detalle de venta para ID {id}: {detalle}")

        # Separa los datos de la venta y los productos para el template
        venta = {
            "idVenta": detalle["idVenta"],
            "fechaVenta": detalle["fechaVenta"],
            "total": detalle["total"],
        }
        productos = detalle["productos"]

        return render_template('detalle_venta.html', venta=venta, productos=productos)
    except Exception as e:
        flash(f"Error al cargar los detalles de la venta: {e}", 'danger')
        return redirect(url_for('ventas'))


@app.route('/total_ventas', methods=['GET'])
def total_ventas():
    try:
        ventas_data = GET_Services.get_total_ventas()

        if not ventas_data:
            flash("No hay datos de ventas disponibles.", "danger")
            return redirect(url_for('dashboard_admin'))

        total_ventas = ventas_data['totalVentas']
        productos = [
            {
                "nombreProducto": p["nombreProducto"],
                "totalCantidad": p["totalCantidad"],
                "totalPrecio": p["totalIngresos"]  # Cambia 'totalPrecio' por 'totalIngresos'
            }
            for p in ventas_data['productos']
        ]

        return render_template('total_ventas.html', total_ventas=total_ventas, productos=productos)
    except Exception as e:
        flash(f"Error al cargar el total de las ventas: {e}", "danger")
        return redirect(url_for('dashboard_admin'))



@app.route('/ventas', methods=['GET'])
def ventas():
    try:
        ventas_data = GET_Services.get_ventas()

        if not ventas_data:
            flash("No hay datos de ventas disponibles.", "danger")
            return redirect(url_for('dashboard_admin'))

        # Convertir las fechas en el backend
        for venta in ventas_data:
            venta['fechaVenta'] = datetime.fromisoformat(venta['fechaVenta']).strftime('%Y-%m-%d %I:%M %p')

        return render_template('ventas.html', ventas=ventas_data)
    except Exception as e:
        flash(f"Error al cargar las ventas: {e}", "danger")
        return redirect(url_for('dashboard_admin'))
