import requests

class GET_Service:
    def __init__(self, base_url):
        self.base_url = base_url

    def get_categorias(self):
        response = requests.get(f"{self.base_url}/categoria", verify=False)
        response.raise_for_status()
        categorias = response.json()
        print("Datos obtenidos de categorías:", categorias)
        return categorias
    
    def get_productos(self):
        response = requests.get(f"{self.base_url}/productos", verify=False)
        response.raise_for_status()
        productos = response.json()
        print("Datos obtenidos de productos:", productos)
        return productos
    
    def get_detalle_venta(self, id_venta):
        """
        Obtiene el detalle de una venta específica desde la API.
        """
        url = f"{self.base_url}/detalle_venta/{id_venta}"  # Verifica que coincida con tu backend
        response = requests.get(url, verify=False)  # Deshabilita la verificación del SSL si estás usando HTTPS local
        response.raise_for_status()
        detalle = response.json()
        print(f"Detalle de la venta {id_venta}: {detalle}")
        return detalle


    def get_total_ventas(self):
        """
        Obtiene el total de ventas acumuladas y el desglose de ingresos por producto.
        """
        url = f"{self.base_url}/total_ventas"  # Ajustado al endpoint correcto
        response = requests.get(url, verify=False)
        response.raise_for_status()
        total_ventas = response.json()
        print(f"Total de ventas y desglose: {total_ventas}")
        return total_ventas
    
    def get_ventas(self):
        """
        Obtiene todas las ventas desde el API.
        """
        url = f"{self.base_url}/ventas"
        response = requests.get(url, verify=False)
        response.raise_for_status()
        ventas = response.json()
        print(f"Ventas obtenidas: {ventas}")
        return ventas




class POST_Service:
    def __init__(self, base_url):
        self.base_url = base_url

    def create_producto(self, data):
        response = requests.post(f"{self.base_url}/productos", json=data, verify=False)
        response.raise_for_status()
        return response.json()

    def create_categoria(self, data):
        response = requests.post(f"{self.base_url}/categoria", json=data, verify=False)  
        response.raise_for_status()
        return response.json()

    
    

class AdministradorService:
    def __init__(self, base_url):
        self.base_url = base_url

    def get_administrador_por_correo(self, correo):
        """
        Obtiene un administrador por su correo.
        """
        try:
            response = requests.get(f"{self.base_url}/administradores?correo={correo}", verify=False)
            response.raise_for_status()  # Lanza error si la solicitud no es exitosa
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error al obtener el administrador: {e}")
            return None
        

class DeleteService:
    def __init__(self, base_url):
        self.base_url = base_url

    def delete_producto(self, producto_id):
        """
        Elimina un producto por su ID utilizando la API de DELETE.
        """
        url = f"{self.base_url}/productos/{producto_id}"
        response = requests.delete(url, verify=False)
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 404:
            raise ValueError("Producto no encontrado")
        else:
            response.raise_for_status()

    def delete_categoria(self, categoria_id):
        """
        Elimina una categoría por su ID utilizando la API de DELETE.
        """
        url = f"{self.base_url}/categoria/{categoria_id}"
        response = requests.delete(url, verify=False)
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 404:
            raise ValueError("Categoría no encontrada")
        else:
            response.raise_for_status()

class PUT_Service:
    def __init__(self, base_url):
        self.base_url = base_url

    def update_categoria(self, id, data):
        """
        Actualiza una categoría por su ID.
        """
        url = f"{self.base_url}/categoria/{id}"
        response = requests.put(url, json=data, verify=False)
        
        # Si el backend responde con 204 (sin contenido)
        if response.status_code == 204:
            return {"message": "Producto actualizado correctamente"}
        elif response.status_code == 200 and response.text.strip():
            return response.json()
        
        response.raise_for_status()

    def update_producto(self, id, data):
        url = f"{self.base_url}/productos/{id}"
        response = requests.put(url, json=data, verify=False)

        # Si el backend responde con 204 (sin contenido)
        if response.status_code == 204:
            return {"message": "Producto actualizado correctamente"}
        elif response.status_code == 200 and response.text.strip():
            return response.json()
        
        response.raise_for_status()


