from app import db

# Modelo de Categoría
class Categoria(db.Model):
    __tablename__ = 'categorias'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False, unique=True)
    categoria_update = db.Column(db.String(50), nullable=True)


# Modelo de Producto
class Producto(db.Model):
    __tablename__ = 'productos'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    precio = db.Column(db.Float, nullable=False)
    cantidad_en_stock = db.Column(db.Integer, nullable=False)
    producto_update = db.Column(db.String(50), nullable=True)
    id_categoria = db.Column(db.Integer, db.ForeignKey('categorias.id'), nullable=False)

    categoria = db.relationship('Categoria', backref=db.backref('productos', lazy=True))


# Modelo para las Categorías eliminadas (Lógica de eliminación)
class DeleteCategorias(db.Model):
    __tablename__ = 'delete_categorias'

    id = db.Column('IdCategoria', db.Integer, primary_key=True)
    nombre = db.Column('NombreCategoria', db.String(50), nullable=False, unique=True)
    categoria_update = db.Column('Categoria_Update', db.String(50), nullable=True)
    eliminado = db.Column('DeleteAt', db.String(50))


# Modelo para los Productos eliminados (Lógica de eliminación)
class DeleteProductos(db.Model):
    __tablename__ = 'delete_productos'

    id = db.Column('IdProducto', db.Integer, primary_key=True)
    nombre = db.Column('NombreProducto', db.String(50), nullable=False, unique=True)
    producto_update = db.Column('Producto_Update', db.String(50), nullable=True)
    eliminado = db.Column('DeleteAt', db.String(50))


# Modelo de Usuario
class Usuario(db.Model):
    __tablename__ = 'usuarios'

    id = db.Column(db.Integer, primary_key=True)
    usuario = db.Column(db.String(50), nullable=False, unique=True)
    contrasena = db.Column(db.String(50), nullable=False)
    rol = db.Column(db.String(20), nullable=False)  # 'admin' o 'cliente'


# Modelo de Venta
class Venta(db.Model):
    __tablename__ = 'ventas'

    id = db.Column(db.Integer, primary_key=True)
    total = db.Column(db.Float, nullable=False)
    fecha = db.Column(db.String(50), nullable=False)  # Puedes usar un tipo de fecha según lo necesites
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)

    usuario = db.relationship('Usuario', backref=db.backref('ventas', lazy=True))


# Modelo de Detalle de Venta
class DetalleVenta(db.Model):
    __tablename__ = 'detalle_venta'

    id = db.Column(db.Integer, primary_key=True)
    id_venta = db.Column(db.Integer, db.ForeignKey('ventas.id'), nullable=False)
    id_producto = db.Column(db.Integer, db.ForeignKey('productos.id'), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    precio = db.Column(db.Float, nullable=False)

    venta = db.relationship('Venta', backref=db.backref('detalles', lazy=True))
    producto = db.relationship('Producto', backref=db.backref('detalles', lazy=True))
