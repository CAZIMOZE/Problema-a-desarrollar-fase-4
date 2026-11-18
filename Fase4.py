#Sistema Integral de Gestión - Software FJ
#Programación Orientada a Objetos (POO) y Manejo Avanzado de Excepciones.
#Sin uso de bases de datos; persistencia de eventos y errores mediante archivos de log.

# Herramientas para definir clases abstractas y métodos obligatorios (Abstracción)
from abc import ABC, abstractmethod

# Manejo de fechas y horas exactas para registros de logs y marcas de tiempo en reservas
from datetime import datetime

# Gestión de rutas y directorios del sistema operativo para almacenar los archivos de log
import os

# Expresiones regulares para validar formatos estrictos (correos, teléfonos, documentos)
import re


#Parte : SISTEMA DE REGISTRO DE EVENTOS Y ERRORES (LOGS)


class GestorLogs:
    
    #Clase encargada de registrar todos los eventos informativos y errores
    #del sistema en un archivo de texto (.log) sin detener la ejecución.
    
    def __init__(self, carpeta: str = "logs", nombre_archivo: str = "software_fj.log"):
        #Se encapsula la ruta del archivo de logs
        self.__carpeta = carpeta
        self.__ruta_archivo = os.path.join(carpeta, nombre_archivo)
        self.__inicializar_directorio()

    def __inicializar_directorio(self) -> None:
        #Se verifica si la carpeta de logs existe; si no, la crea de forma segura.
        try:
            if not os.path.exists(self.__carpeta):
                os.makedirs(self.__carpeta)
        except OSError as e:
            print(f"[CRÍTICO DE SISTEMA] No se pudo crear el directorio de logs: {e}")

    def registrar(self, nivel: str, mensaje: str) -> None:
        #Se escribe una línea en el archivo de log usando try/except/finally
        #para garantizar el manejo seguro del archivo.
        
        marca_tiempo = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        linea_log = f"[{marca_tiempo}] [{nivel.upper()}] {mensaje}\n"
        archivo = None

        try:
            #Se abre el archivo en modo 'a' (append) para agregar sin borrar lo anterior
            archivo = open(self.__ruta_archivo, mode="a", encoding="utf-8")
            archivo.write(linea_log)
        except IOError as error_io:
            #Si falla el disco o los permisos, informamos en consola pero no caemos
            print(f"[FALLO LOG] No se pudo escribir en el archivo de log: {error_io}")
        finally:
            #El bloque finally siempre se ejecuta para liberar el recurso del archivo
            if archivo is not None and not archivo.closed:
                archivo.close()

    def info(self, mensaje: str) -> None:
        #Atajo para registrar operaciones exitosas o eventos normales.
        self.registrar("INFO", mensaje)

    def error(self, mensaje: str) -> None:
        #Atajo para registrar excepciones, validaciones fallidas o errores.
        self.registrar("ERROR", mensaje)

#Parte 2: JERARQUÍA DE EXCEPCIONES PERSONALIZADAS

class SoftwareFJError(Exception):
    #Excepción base de todo el sistema Software FJ.
    #Permite capturar cualquier error de negocio del sistema de forma unificada
    #y conservar la marca de tiempo del incidente.
    
    def __init__(self, mensaje: str, codigo: str = "ERR-GENERAL"):
        self.mensaje = mensaje
        self.codigo = codigo
        self.fecha_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        super().__init__(f"[{self.codigo}] {self.mensaje}")


class DatosInvalidosError(SoftwareFJError):
    #Se lanza cuando un cliente, servicio o reserva recibe datos con formato o valor inválido."""
    def __init__(self, mensaje: str):
        super().__init__(mensaje, codigo="ERR-DATOS")


class ParametroFaltanteError(SoftwareFJError):
    #Se lanza cuando se omite un dato obligatorio requerido para operar."""
    def __init__(self, mensaje: str):
        super().__init__(mensaje, codigo="ERR-PARAMETRO")


class ServicioNoDisponibleError(SoftwareFJError):
    #Se lanza cuando se intenta reservar una sala, equipo o asesoría sin cupo o inactiva."""
    def __init__(self, mensaje: str):
        super().__init__(mensaje, codigo="ERR-DISPONIBILIDAD")


class ReservaInvalidaError(SoftwareFJError):
    #Se lanza ante intentos de reserva incorrectos (duración nula, cliente inexistente, etc.)."""
    def __init__(self, mensaje: str):
        super().__init__(mensaje, codigo="ERR-RESERVA")


class OperacionNoPermitidaError(SoftwareFJError):
    #Se lanza al intentar transiciones de estado ilegales (ej. cancelar una reserva ya cancelada)."""
    def __init__(self, mensaje: str):
        super().__init__(mensaje, codigo="ERR-OPERACION")


class CalculoInconsistenteError(SoftwareFJError):
    #Se lanza cuando un cálculo de tarifas, impuestos o descuentos da un resultado incoherente."""
    def __init__(self, mensaje: str):
        super().__init__(mensaje, codigo="ERR-CALCULO")


# FASE 4: CLASE ABSTRACTA BASE (ENTIDAD DEL SISTEMA)

class EntidadSistema(ABC):
    #Clase abstracta base para todas las entidades del software (Clientes, Servicios, etc.).
    #Aplica el principio de Abstracción y encapsula atributos comunes como el ID.
    
    
    def __init__(self, id_entidad: str):
        if not id_entidad or not id_entidad.strip():
            raise ParametroFaltanteError("El identificador de la entidad no puede estar vacío.")
        self.__id_entidad = id_entidad.strip()

    @property
    def id_entidad(self) -> str:
        #Permite consultar el ID de forma segura mediante encapsulación (getter)."""
        return self.__id_entidad

    @abstractmethod
    def obtener_resumen(self) -> str:
        #Método abstracto obligatorio. 
        #Cada clase hija debe implementar su propia versión para retornar los detalles.
        pass