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


#Parte 2 : SISTEMA DE REGISTRO DE EVENTOS Y ERRORES (LOGS)


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

#Parte 3: JERARQUÍA DE EXCEPCIONES PERSONALIZADAS

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


#Parte 4: CLASE ABSTRACTA BASE (ENTIDAD DEL SISTEMA)

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

 
#Parte 5: CLASE CLIENTE (HERENCIA DE ENTIDAD Y VALIDACIONES ESTRICTAS)

class Cliente(EntidadSistema):
    #Representa a un cliente dentro de Software FJ.
    #Hereda de EntidadSistema e implementa validaciones estrictas de datos personales.
        
    def __init__(self, id_cliente: str, nombre: str, correo: str, telefono: str):
        super().__init__(id_cliente)
        
        #Valida y asigna nombre
        if not nombre or not nombre.strip():
            raise ParametroFaltanteError("El nombre del cliente es obligatorio.")
        self.__nombre = nombre.strip()
        
        #Valida el formato de correo electrónico mediante expresiones regulares
        if not correo or not correo.strip():
            raise ParametroFaltanteError("El correo electrónico es obligatorio.")
        patron_correo = r"^[\w\.-]+@[\w\.-]+\.\w+$"
        if not re.match(patron_correo, correo.strip()):
            raise DatosInvalidosError(f"El formato del correo electrónico '{correo}' no es válido.")
        self.__correo = correo.strip().lower()
        
        #Valida teléfono (mínimo 7 dígitos numéricos)
        if not telefono or not telefono.strip():
            raise ParametroFaltanteError("El teléfono del cliente es obligatorio.")
        telefono_limpio = re.sub(r"\D", "", telefono) # Elimina espacios, guiones o símbolos
        if len(telefono_limpio) < 7:
            raise DatosInvalidosError(f"El teléfono '{telefono}' debe contener al menos 7 dígitos válidos.")
        self.__telefono = telefono_limpio

    @property
    def nombre(self) -> str:
        return self.__nombre

    @property
    def correo(self) -> str:
        return self.__correo

    @property
    def telefono(self) -> str:
        return self.__telefono

    def obtener_resumen(self) -> str:
        #Implementación obligatoria del método abstracto de EntidadSistema."""
        return (f"Cliente [ID: {self.id_entidad}] | Nombre: {self.__nombre} | "
                f"Correo: {self.__correo} | Teléfono: {self.__telefono}")


# Parte 6: CLASE ABSTRACTA SERVICIO (BASE PARA SERVICIOS ESPECIALIZADOS)

class Servicio(EntidadSistema):
    
    #Clase abstracta base para los servicios ofrecidos por Software FJ.
    #Hereda de EntidadSistema y establece la interfaz común de costos y disponibilidad.
   
    def __init__(self, id_servicio: str, nombre: str, tarifa_base: float, disponible: bool = True):
        super().__init__(id_servicio)

        if not nombre or not nombre.strip():
            raise ParametroFaltanteError("El nombre del servicio es obligatorio.")
        self.__nombre = nombre.strip()

        if tarifa_base is None or tarifa_base <= 0:
            raise DatosInvalidosError(
                f"La tarifa base del servicio '{self.__nombre}' debe ser mayor que cero."
            )
        self.__tarifa_base = float(tarifa_base)
        self.__disponible = bool(disponible)

    @property
    def nombre(self) -> str:
        return self.__nombre

    @property
    def tarifa_base(self) -> float:
        return self.__tarifa_base

    @property
    def disponible(self) -> bool:
        return self.__disponible

    def cambiar_disponibilidad(self, estado: bool) -> None:
        #Actualiza de forma controlada si el servicio está disponible o no."""
        self.__disponible = bool(estado)

    @abstractmethod
    def verificar_disponibilidad(self, cantidad: int = 1) -> bool:
        #Verifica si el servicio puede atender la cantidad/cupo solicitada."""
        pass

    @abstractmethod
    def calcular_costo(self, unidades: float, **kwargs) -> float:
        #Calcula el costo total de un servicio.
        #Soporta argumentos adicionales (kwargs) para simular sobrecarga según el servicio.
       
        pass

    def obtener_resumen(self) -> str:
        #Implementación obligatoria del método abstracto de EntidadSistema.
        estado_texto = "Disponible" if self.__disponible else "No disponible"
        return (f"Servicio [ID: {self.id_entidad}] | Nombre: {self.__nombre} | "
                f"Tarifa base: ${self.__tarifa_base:,.2f} | Estado: {estado_texto}")


# Parte 7: SERVICIO ESPECIALIZADO RESERVA DE SALA

class ReservaSala(Servicio):
    #Servicio especializado para la reserva de salas de reuniones, conferencias o talleres.
    #Hereda de Servicio e incorpora control de capacidad y equipamiento audiovisual.
 
    def __init__(
        self,
        id_servicio: str,
        nombre: str,
        tarifa_base: float,
        capacidad_maxima: int,
        tiene_audiovisual: bool = False,
        recargo_audiovisual: float = 0.15,
        disponible: bool = True,
    ):
        super().__init__(id_servicio, nombre, tarifa_base, disponible)

        if capacidad_maxima is None or capacidad_maxima <= 0:
            raise DatosInvalidosError(
                f"La capacidad máxima de la sala '{self.nombre}' debe ser mayor que cero."
            )
        if recargo_audiovisual < 0:
            raise DatosInvalidosError(
                "El porcentaje de recargo por equipo audiovisual no puede ser negativo."
            )

        self.__capacidad_maxima = int(capacidad_maxima)
        self.__tiene_audiovisual = bool(tiene_audiovisual)
        self.__recargo_audiovisual = float(recargo_audiovisual)

    @property
    def capacidad_maxima(self) -> int:
        return self.__capacidad_maxima

    @property
    def tiene_audiovisual(self) -> bool:
        return self.__tiene_audiovisual

    @property
    def recargo_audiovisual(self) -> float:
        return self.__recargo_audiovisual

    def verificar_disponibilidad(self, cantidad: int = 1) -> bool:
        #rifica si la sala está disponible y soporta la cantidad de asistentes solicitada.
        if cantidad is None or cantidad <= 0:
            raise DatosInvalidosError("La cantidad de asistentes para la sala debe ser mayor que cero.")

        if not self.disponible:
            raise ServicioNoDisponibleError(
                f"La sala '{self.nombre}' [ID: {self.id_entidad}] no se encuentra disponible."
            )

        if cantidad > self.__capacidad_maxima:
            raise ServicioNoDisponibleError(
                f"La sala '{self.nombre}' admite máximo {self.__capacidad_maxima} personas "
                f"(solicitadas: {cantidad})."
            )

        return True

    def calcular_costo(self, unidades: float, **kwargs) -> float:
#        Calcula el costo total de la reserva de sala según horas (unidades).
        #Soporta 'incluir_audiovisual' (bool) y 'descuento_porcentaje' (float) vía kwargs.
        if unidades is None or unidades <= 0:
            raise DatosInvalidosError("La cantidad de horas de reserva debe ser mayor que cero.")

        incluir_audiovisual = bool(kwargs.get("incluir_audiovisual", self.__tiene_audiovisual))
        descuento_porcentaje = float(kwargs.get("descuento_porcentaje", 0.0))

        if descuento_porcentaje < 0 or descuento_porcentaje >= 100:
            raise CalculoInconsistenteError(
                f"El porcentaje de descuento '{descuento_porcentaje}' es inconsistente."
            )

        subtotal = float(unidades) * self.tarifa_base

        if incluir_audiovisual:
            if not self.__tiene_audiovisual and kwargs.get("incluir_audiovisual") is True:
                raise OperacionNoPermitidaError(
                    f"La sala '{self.nombre}' no cuenta con equipamiento audiovisual instalado."
                )
            subtotal += subtotal * self.__recargo_audiovisual

        total = subtotal * (1 - (descuento_porcentaje / 100.0))

        if total <= 0:
            raise CalculoInconsistenteError(
                "El cálculo del costo de la reserva de sala produjo un valor no válido."
            )

        return round(total, 2)

    def obtener_resumen(self) -> str:
        #Retorna el resumen detallado de la sala incluyendo capacidad y audiovisual.
        av_texto = "Con audiovisual" if self.__tiene_audiovisual else "Sin audiovisual"
        base_resumen = super().obtener_resumen()
        return (
            f"{base_resumen} | Tipo: Reserva de Sala | "
            f"Capacidad: {self.__capacidad_maxima} personas | {av_texto}"
        )


# Parte 8: SERVICIO ESPECIALIZADO ALQUILER DE EQUIPO

class AlquilerEquipo(Servicio):
    #Servicio especializado para el alquiler de equipos tecnológicos.
    #Hereda de Servicio e incorpora control de stock y seguro obligatorio.

    def __init__(
        self,
        id_servicio: str,
        nombre: str,
        tarifa_base: float,
        stock_total: int,
        costo_seguro_unidad: float = 0.0,
        stock_disponible: int | None = None,
        disponible: bool = True,
    ):
        super().__init__(id_servicio, nombre, tarifa_base, disponible)

        if stock_total is None or stock_total <= 0:
            raise DatosInvalidosError(
                f"El stock total del equipo '{self.nombre}' debe ser mayor que cero."
            )
        if costo_seguro_unidad is None or costo_seguro_unidad < 0:
            raise DatosInvalidosError(
                f"El costo del seguro por unidad para '{self.nombre}' no puede ser negativo."
            )

        self.__stock_total = int(stock_total)
        self.__costo_seguro_unidad = float(costo_seguro_unidad)

        if stock_disponible is None:
            self.__stock_disponible = self.__stock_total
        else:
            if stock_disponible < 0 or stock_disponible > self.__stock_total:
                raise DatosInvalidosError(
                    f"El stock disponible ({stock_disponible}) para '{self.nombre}' "
                    f"debe estar entre 0 y {self.__stock_total}."
                )
            self.__stock_disponible = int(stock_disponible)

    @property
    def stock_total(self) -> int:
        return self.__stock_total

    @property
    def stock_disponible(self) -> int:
        return self.__stock_disponible

    @property
    def costo_seguro_unidad(self) -> float:
        return self.__costo_seguro_unidad

    def reservar_unidades(self, cantidad: int) -> None:
        #Descuenta unidades del stock disponible de forma controlada.
        self.verificar_disponibilidad(cantidad)
        self.__stock_disponible -= int(cantidad)
        if self.__stock_disponible == 0:
            self.cambiar_disponibilidad(False)

    def liberar_unidades(self, cantidad: int) -> None:
        #Devuelve unidades al stock disponible tras finalizar o cancelar una reserva.
        if cantidad is None or cantidad <= 0:
            raise DatosInvalidosError("La cantidad a liberar debe ser mayor que cero.")
        if self.__stock_disponible + int(cantidad) > self.__stock_total:
            raise OperacionNoPermitidaError(
                f"No se pueden liberar {cantidad} unidades de '{self.nombre}': "
                f"superaría el stock total ({self.__stock_total})."
            )
        self.__stock_disponible += int(cantidad)
        if self.__stock_disponible > 0:
            self.cambiar_disponibilidad(True)

    def verificar_disponibilidad(self, cantidad: int = 1) -> bool:
        #Verifica si el servicio está activo y hay suficiente stock para la cantidad solicitada.
        if cantidad is None or cantidad <= 0:
            raise DatosInvalidosError("La cantidad de equipos a consultar debe ser mayor que cero.")

        if not self.disponible or self.__stock_disponible <= 0:
            raise ServicioNoDisponibleError(
                f"El equipo '{self.nombre}' [ID: {self.id_entidad}] no tiene stock disponible."
            )

        if int(cantidad) > self.__stock_disponible:
            raise ServicioNoDisponibleError(
                f"Stock insuficiente para '{self.nombre}': disponibles {self.__stock_disponible}, "
                f"solicitados {cantidad}."
            )

        return True

    def calcular_costo(self, unidades: float, **kwargs) -> float:
        #Calcula el costo total del alquiler según días/horas (unidades), cantidad de equipos
        #y seguro obligatorio por unidad.
        #Soporta 'cantidad_equipos' (int), 'seguro_unidad' (float) y 'descuento_porcentaje' (float).
        
        if unidades is None or unidades <= 0:
            raise DatosInvalidosError("La duración del alquiler debe ser mayor que cero.")

        cantidad_equipos = int(kwargs.get("cantidad_equipos", 1))
        if cantidad_equipos <= 0:
            raise DatosInvalidosError("La cantidad de equipos a alquilar debe ser mayor que cero.")

        seguro_unidad = float(kwargs.get("seguro_unidad", self.__costo_seguro_unidad))
        if seguro_unidad < 0:
            raise CalculoInconsistenteError(
                "El costo del seguro por unidad no puede ser negativo."
            )

        descuento_porcentaje = float(kwargs.get("descuento_porcentaje", 0.0))
        if descuento_porcentaje < 0 or descuento_porcentaje >= 100:
            raise CalculoInconsistenteError(
                f"El porcentaje de descuento '{descuento_porcentaje}' es inconsistente."
            )

        subtotal_alquiler = float(unidades) * self.tarifa_base * cantidad_equipos
        subtotal_seguro = seguro_unidad * cantidad_equipos
        total = (subtotal_alquiler + subtotal_seguro) * (1 - (descuento_porcentaje / 100.0))

        if total <= 0:
            raise CalculoInconsistenteError(
                "El cálculo del costo de alquiler de equipo produjo un valor no válido."
            )

        return round(total, 2)

    def obtener_resumen(self) -> str:
        #Retorna el resumen del equipo con inventario y seguro obligatorio.
        base_resumen = super().obtener_resumen()
        return (
            f"{base_resumen} | Tipo: Alquiler de Equipo | "
            f"Stock: {self.__stock_disponible}/{self.__stock_total} | "
            f"Seguro/unidad: ${self.__costo_seguro_unidad:,.2f}"
        )


# Parte 9: SERVICIO ESPECIALIZADO ASESORÍA ESPECIALIZADA

class AsesoriaEspecializada(Servicio):
    #Servicio especializado para asesorías o consultorías técnicas.
    #Hereda de Servicio e incorpora niveles de complejidad y recargos por urgencia.

    MULTIPLICADORES_COMPLEJIDAD = {
        "BASICA": 1.0,
        "INTERMEDIA": 1.35,
        "AVANZADA": 1.75,
        "CRITICA": 2.25,
    }

    def __init__(
        self,
        id_servicio: str,
        nombre: str,
        tarifa_base: float,
        nivel_complejidad: str = "BASICA",
        recargo_urgencia: float = 0.25,
        cupo_maximo_sesiones: int = 10,
        disponible: bool = True,
    ):
        super().__init__(id_servicio, nombre, tarifa_base, disponible)

        if not nivel_complejidad or not nivel_complejidad.strip():
            raise ParametroFaltanteError("El nivel de complejidad de la asesoría es obligatorio.")

        nivel_normalizado = nivel_complejidad.strip().upper()
        if nivel_normalizado not in self.MULTIPLICADORES_COMPLEJIDAD:
            opciones = ", ".join(self.MULTIPLICADORES_COMPLEJIDAD.keys())
            raise DatosInvalidosError(
                f"Nivel de complejidad '{nivel_complejidad}' no válido. Opciones permitidas: {opciones}."
            )

        if recargo_urgencia is None or recargo_urgencia < 0:
            raise DatosInvalidosError(
                "El porcentaje de recargo por urgencia no puede ser negativo."
            )

        if cupo_maximo_sesiones is None or cupo_maximo_sesiones <= 0:
            raise DatosInvalidosError(
                "El cupo máximo de sesiones para la asesoría debe ser mayor que cero."
            )

        self.__nivel_complejidad = nivel_normalizado
        self.__recargo_urgencia = float(recargo_urgencia)
        self.__cupo_maximo_sesiones = int(cupo_maximo_sesiones)
        self.__sesiones_programadas = 0

    @property
    def nivel_complejidad(self) -> str:
        return self.__nivel_complejidad

    @property
    def recargo_urgencia(self) -> float:
        return self.__recargo_urgencia

    @property
    def cupo_maximo_sesiones(self) -> int:
        return self.__cupo_maximo_sesiones

    @property
    def sesiones_programadas(self) -> int:
        return self.__sesiones_programadas

    def programar_sesion(self, cantidad_sesiones: int = 1) -> None:
        #Registra sesiones programadas verificando primero la disponibilidad.
        self.verificar_disponibilidad(cantidad_sesiones)
        self.__sesiones_programadas += int(cantidad_sesiones)
        if self.__sesiones_programadas >= self.__cupo_maximo_sesiones:
            self.cambiar_disponibilidad(False)

    def liberar_sesion(self, cantidad_sesiones: int = 1) -> None:
        #Libera sesiones canceladas o finalizadas dentro del cupo registrado.
        if cantidad_sesiones is None or cantidad_sesiones <= 0:
            raise DatosInvalidosError("La cantidad de sesiones a liberar debe ser mayor que cero.")
        if int(cantidad_sesiones) > self.__sesiones_programadas:
            raise OperacionNoPermitidaError(
                f"No se pueden liberar {cantidad_sesiones} sesiones: solo hay "
                f"{self.__sesiones_programadas} programadas."
            )
        self.__sesiones_programadas -= int(cantidad_sesiones)
        if self.__sesiones_programadas < self.__cupo_maximo_sesiones:
            self.cambiar_disponibilidad(True)

    def verificar_disponibilidad(self, cantidad: int = 1) -> bool:
        #Verifica si la asesoría está activa y tiene cupo para la cantidad de sesiones solicitadas.
        if cantidad is None or cantidad <= 0:
            raise DatosInvalidosError("La cantidad de sesiones a consultar debe ser mayor que cero.")

        cupo_restante = self.__cupo_maximo_sesiones - self.__sesiones_programadas
        if not self.disponible or cupo_restante <= 0:
            raise ServicioNoDisponibleError(
                f"La asesoría '{self.nombre}' [ID: {self.id_entidad}] no tiene cupos disponibles."
            )

        if int(cantidad) > cupo_restante:
            raise ServicioNoDisponibleError(
                f"Cupo insuficiente para '{self.nombre}': disponibles {cupo_restante} sesiones, "
                f"solicitadas {cantidad}."
            )

        return True

    def calcular_costo(self, unidades: float, **kwargs) -> float:
       #Calcula el costo total de la asesoría según horas/unidades (unidades),
        #complejidad del servicio y recargo por urgencia.
        #Soporta 'urgente' (bool), 'recargo_urgencia' (float) y 'descuento_porcentaje' (float).
        if unidades is None or unidades <= 0:
            raise DatosInvalidosError("La duración en horas de la asesoría debe ser mayor que cero.")

        es_urgente = bool(kwargs.get("urgente", False))
        porcentaje_urgencia = float(kwargs.get("recargo_urgencia", self.__recargo_urgencia))
        if porcentaje_urgencia < 0:
            raise CalculoInconsistenteError(
                "El porcentaje de recargo por urgencia no puede ser negativo."
            )

        descuento_porcentaje = float(kwargs.get("descuento_porcentaje", 0.0))
        if descuento_porcentaje < 0 or descuento_porcentaje >= 100:
            raise CalculoInconsistenteError(
                f"El porcentaje de descuento '{descuento_porcentaje}' es inconsistente."
            )

        factor_complejidad = self.MULTIPLICADORES_COMPLEJIDAD[self.__nivel_complejidad]
        subtotal = float(unidades) * self.tarifa_base * factor_complejidad

        if es_urgente:
            subtotal += subtotal * porcentaje_urgencia

        total = subtotal * (1 - (descuento_porcentaje / 100.0))

        if total <= 0:
            raise CalculoInconsistenteError(
                "El cálculo del costo de la asesoría especializada produjo un valor no válido."
            )

        return round(total, 2)

    def obtener_resumen(self) -> str:
        #Retorna el resumen de la asesoría con complejidad, recargo por urgencia y cupo.
        base_resumen = super().obtener_resumen()
        return (
            f"{base_resumen} | Tipo: Asesoría Especializada | "
            f"Complejidad: {self.__nivel_complejidad} | "
            f"Recargo urgencia: {self.__recargo_urgencia * 100:.0f}% | "
            f"Sesiones: {self.__sesiones_programadas}/{self.__cupo_maximo_sesiones}"
        )


#Parte 10: CLASE RESERVA (CONTROL DE ESTADOS Y ENCADENAMIENTO DE EXCEPCIONES)

class Reserva:
    #Representa una reserva de servicio realizada por un cliente dentro de Software FJ.
    #Gestiona el ciclo de vida de estados y encadena excepciones con 'raise ... from ...'.

    ESTADOS_VALIDOS = ("PENDIENTE", "CONFIRMADA", "CANCELADA")

    def __init__(
        self,
        id_reserva: str,
        cliente: Cliente,
        servicio: Servicio,
        unidades: float,
        cantidad: int = 1,
        **parametros_costo,
    ):
        if not id_reserva or not id_reserva.strip():
            raise ParametroFaltanteError("El identificador de la reserva es obligatorio.")

        if not isinstance(cliente, Cliente):
            raise DatosInvalidosError("La reserva requiere una instancia válida de Cliente.")

        if not isinstance(servicio, Servicio):
            raise DatosInvalidosError("La reserva requiere una instancia válida de Servicio.")

        if unidades is None or unidades <= 0:
            raise ReservaInvalidaError("Las unidades o duración de la reserva deben ser mayores que cero.")

        if cantidad is None or cantidad <= 0:
            raise ReservaInvalidaError("La cantidad solicitada en la reserva debe ser mayor que cero.")

        self.__id_reserva = id_reserva.strip()
        self.__cliente = cliente
        self.__servicio = servicio
        self.__unidades = float(unidades)
        self.__cantidad = int(cantidad)
        self.__parametros_costo = dict(parametros_costo)
        self.__estado = "PENDIENTE"

        try:
            self.__servicio.verificar_disponibilidad(self.__cantidad)
            self.__costo_total = self.__servicio.calcular_costo(
                self.__unidades, **self.__parametros_costo
            )
        except SoftwareFJError as exc:
            raise ReservaInvalidaError(
                f"No fue posible crear la reserva '{self.__id_reserva}' para el cliente "
                f"'{self.__cliente.nombre}' en el servicio '{self.__servicio.nombre}'."
            ) from exc

    @property
    def id_reserva(self) -> str:
        return self.__id_reserva

    @property
    def cliente(self) -> Cliente:
        return self.__cliente

    @property
    def servicio(self) -> Servicio:
        return self.__servicio

    @property
    def unidades(self) -> float:
        return self.__unidades

    @property
    def cantidad(self) -> int:
        return self.__cantidad

    @property
    def estado(self) -> str:
        return self.__estado

    @property
    def costo_total(self) -> float:
        return self.__costo_total

    def confirmar(self) -> None:
        #Confirma una reserva pendiente y aplica el consumo correspondiente en el servicio.
        if self.__estado == "CONFIRMADA":
            raise OperacionNoPermitidaError(
                f"La reserva '{self.__id_reserva}' ya se encuentra CONFIRMADA."
            )
        if self.__estado == "CANCELADA":
            raise OperacionNoPermitidaError(
                f"No se puede confirmar la reserva '{self.__id_reserva}' porque está CANCELADA."
            )

        try:
            self.__servicio.verificar_disponibilidad(self.__cantidad)
            self.__costo_total = self.__servicio.calcular_costo(
                self.__unidades, **self.__parametros_costo
            )

            if isinstance(self.__servicio, AlquilerEquipo):
                self.__servicio.reservar_unidades(self.__cantidad)
            elif isinstance(self.__servicio, AsesoriaEspecializada):
                self.__servicio.programar_sesion(self.__cantidad)

            self.__estado = "CONFIRMADA"
        except SoftwareFJError as exc:
            raise ReservaInvalidaError(
                f"Error al confirmar la reserva '{self.__id_reserva}'."
            ) from exc

    def cancelar(self) -> None:
        #Cancela una reserva activa y libera recursos si ya había sido confirmada.
        if self.__estado == "CANCELADA":
            raise OperacionNoPermitidaError(
                f"La reserva '{self.__id_reserva}' ya se encuentra CANCELADA."
            )

        try:
            if self.__estado == "CONFIRMADA":
                if isinstance(self.__servicio, AlquilerEquipo):
                    self.__servicio.liberar_unidades(self.__cantidad)
                elif isinstance(self.__servicio, AsesoriaEspecializada):
                    self.__servicio.liberar_sesion(self.__cantidad)

            self.__estado = "CANCELADA"
        except SoftwareFJError as exc:
            raise OperacionNoPermitidaError(
                f"No fue posible cancelar limpiamente la reserva '{self.__id_reserva}'."
            ) from exc

    def obtener_resumen(self) -> str:
        #Retorna un resumen legible del estado y costo de la reserva.
        return (
            f"Reserva [ID: {self.__id_reserva}] | Estado: {self.__estado} | "
            f"Cliente: {self.__cliente.nombre} ({self.__cliente.id_entidad}) | "
            f"Servicio: {self.__servicio.nombre} | Unidades: {self.__unidades} | "
            f"Cantidad: {self.__cantidad} | Total: ${self.__costo_total:,.2f}"
        )


# Parte 11: MOTOR CENTRAL SISTEMA SOFTWARE FJ (GESTIÓN EN MEMORIA Y LOGS)

class SistemaSoftwareFJ:
    #Motor central en memoria de Software FJ.
    #Coordina clientes, servicios, reservas y registro de eventos/errores en GestorLogs.

    def __init__(self, gestor_logs: GestorLogs | None = None):
        self.__logs = gestor_logs if isinstance(gestor_logs, GestorLogs) else GestorLogs()
        self.__clientes: dict[str, Cliente] = {}
        self.__servicios: dict[str, Servicio] = {}
        self.__reservas: dict[str, Reserva] = {}
        self.__logs.registrar_evento("INFO", "SistemaSoftwareFJ inicializado correctamente.")

    @property
    def clientes(self) -> dict[str, Cliente]:
        return dict(self.__clientes)

    @property
    def servicios(self) -> dict[str, Servicio]:
        return dict(self.__servicios)

    @property
    def reservas(self) -> dict[str, Reserva]:
        return dict(self.__reservas)

    def _registrar_excepcion(self, contexto: str, exc: Exception) -> None:
        #Registra una excepción y su causa encadenada (si existe) en el archivo de logs.
        detalle = f"{contexto} -> {type(exc).__name__}: {exc}"
        if getattr(exc, "__cause__", None) is not None:
            causa = exc.__cause__
            detalle += f" | Causa raíz: {type(causa).__name__}: {causa}"
        self.__logs.registrar_evento("ERROR", detalle)

    def registrar_cliente(self, cliente: Cliente) -> Cliente:
        #Registra un nuevo cliente en memoria validando duplicados por ID.
        try:
            if not isinstance(cliente, Cliente):
                raise DatosInvalidosError("Solo se pueden registrar objetos de tipo Cliente.")

            if cliente.id_entidad in self.__clientes:
                raise OperacionNoPermitidaError(
                    f"Ya existe un cliente registrado con el ID '{cliente.id_entidad}'."
                )

            self.__clientes[cliente.id_entidad] = cliente
            self.__logs.registrar_evento(
                "INFO", f"Cliente registrado: {cliente.id_entidad} - {cliente.nombre}"
            )
            return cliente
        except SoftwareFJError as exc:
            self._registrar_excepcion("Fallo al registrar cliente", exc)
            raise

    def registrar_servicio(self, servicio: Servicio) -> Servicio:
        #Registra un servicio especializado en memoria validando duplicados por ID.
        try:
            if not isinstance(servicio, Servicio):
                raise DatosInvalidosError("Solo se pueden registrar objetos de tipo Servicio.")

            if servicio.id_entidad in self.__servicios:
                raise OperacionNoPermitidaError(
                    f"Ya existe un servicio registrado con el ID '{servicio.id_entidad}'."
                )

            self.__servicios[servicio.id_entidad] = servicio
            self.__logs.registrar_evento(
                "INFO",
                f"Servicio registrado: {servicio.id_entidad} - {servicio.nombre} ({type(servicio).__name__})",
            )
            return servicio
        except SoftwareFJError as exc:
            self._registrar_excepcion("Fallo al registrar servicio", exc)
            raise

    def crear_reserva(
        self,
        id_reserva: str,
        id_cliente: str,
        id_servicio: str,
        unidades: float,
        cantidad: int = 1,
        **parametros_costo,
    ) -> Reserva:
        #Crea y almacena una reserva validando existencia de cliente, servicio e ID único.
        try:
            if not id_reserva or not id_reserva.strip():
                raise ParametroFaltanteError("El ID de la reserva es obligatorio.")

            id_reserva_limpio = id_reserva.strip()
            if id_reserva_limpio in self.__reservas:
                raise OperacionNoPermitidaError(
                    f"Ya existe una reserva registrada con el ID '{id_reserva_limpio}'."
                )

            if id_cliente not in self.__clientes:
                raise ReservaInvalidaError(
                    f"No se puede crear la reserva '{id_reserva_limpio}': el cliente '{id_cliente}' no existe."
                )

            if id_servicio not in self.__servicios:
                raise ReservaInvalidaError(
                    f"No se puede crear la reserva '{id_reserva_limpio}': el servicio '{id_servicio}' no existe."
                )

            cliente = self.__clientes[id_cliente]
            servicio = self.__servicios[id_servicio]

            reserva = Reserva(
                id_reserva=id_reserva_limpio,
                cliente=cliente,
                servicio=servicio,
                unidades=unidades,
                cantidad=cantidad,
                **parametros_costo,
            )

            self.__reservas[id_reserva_limpio] = reserva
            self.__logs.registrar_evento(
                "INFO",
                f"Reserva creada: {reserva.id_reserva} | Cliente: {cliente.id_entidad} | "
                f"Servicio: {servicio.id_entidad} | Total: ${reserva.costo_total:,.2f}",
            )
            return reserva
        except SoftwareFJError as exc:
            self._registrar_excepcion(f"Fallo al crear reserva '{id_reserva}'", exc)
            raise

    def confirmar_reserva(self, id_reserva: str) -> Reserva:
        #Confirma una reserva existente y registra el evento o error en los logs.
        try:
            if id_reserva not in self.__reservas:
                raise ReservaInvalidaError(f"La reserva '{id_reserva}' no existe en el sistema.")

            reserva = self.__reservas[id_reserva]
            reserva.confirmar()
            self.__logs.registrar_evento(
                "INFO",
                f"Reserva confirmada: {reserva.id_reserva} | Estado: {reserva.estado} | "
                f"Total: ${reserva.costo_total:,.2f}",
            )
            return reserva
        except SoftwareFJError as exc:
            self._registrar_excepcion(f"Fallo al confirmar reserva '{id_reserva}'", exc)
            raise

    def cancelar_reserva(self, id_reserva: str) -> Reserva:
        #Cancela una reserva existente y registra la operación o el error en los logs.
        try:
            if id_reserva not in self.__reservas:
                raise ReservaInvalidaError(f"La reserva '{id_reserva}' no existe en el sistema.")

            reserva = self.__reservas[id_reserva]
            reserva.cancelar()
            self.__logs.registrar_evento(
                "INFO",
                f"Reserva cancelada: {reserva.id_reserva} | Estado: {reserva.estado}",
            )
            return reserva
        except SoftwareFJError as exc:
            self._registrar_excepcion(f"Fallo al cancelar reserva '{id_reserva}'", exc)
            raise

    def obtener_estado_general(self) -> str:
        #Genera un resumen consolidado del estado actual del sistema en memoria.
        lineas = [
            "=== RESUMEN GENERAL - SISTEMA SOFTWARE FJ ===",
            f"Clientes registrados: {len(self.__clientes)}",
            f"Servicios registrados: {len(self.__servicios)}",
            f"Reservas registradas: {len(self.__reservas)}",
            "--- Servicios ---",
        ]
        for srv in self.__servicios.values():
            lineas.append(f"  * {srv.obtener_resumen()}")

        lineas.append("--- Reservas ---")
        for res in self.__reservas.values():
            lineas.append(f"  * {res.obtener_resumen()}")

        return "\n".join(lineas)


#Parte 12: PRUEBAS DE BORDES Y VERIFICACIÓN DE EXCEPCIONES ENCADENADAS

def ejecutar_pruebas_bordes(sistema: SistemaSoftwareFJ) -> list[dict[str, str]]:
    #Ejecuta pruebas de casos límite y verifica el encadenamiento de excepciones
    #registrando cada resultado en el gestor de logs del sistema.
    resultados: list[dict[str, str]] = []

    def _probar(nombre_caso: str, accion) -> None:
        try:
            accion()
            mensaje = f"[FALLO DE PRUEBA] '{nombre_caso}' no lanzó la excepción esperada."
            sistema._SistemaSoftwareFJ__logs.registrar_evento("WARN", mensaje)
            resultados.append({"caso": nombre_caso, "estado": "FALLO", "detalle": mensaje})
        except SoftwareFJError as exc:
            causa_nombre = type(exc.__cause__).__name__ if exc.__cause__ else "Ninguna"
            detalle = (
                f"Capturada {type(exc).__name__} ({exc.codigo}) | "
                f"Causa encadenada: {causa_nombre} | Mensaje: {exc}"
            )
            resultados.append({"caso": nombre_caso, "estado": "OK", "detalle": detalle})

    # 1. Cliente con ID vacío y correo/teléfono inválidos
    _probar(
        "Cliente con ID vacío",
        lambda: Cliente("", "Ana Torres", "ana@correo.com", "3001234567"),
    )
    _probar(
        "Cliente con correo inválido",
        lambda: Cliente("CLI-B1", "Ana Torres", "correo_sin_arroba", "3001234567"),
    )
    _probar(
        "Cliente con teléfono corto",
        lambda: Cliente("CLI-B2", "Ana Torres", "ana@correo.com", "123"),
    )

    # 2. Servicios con valores límite inválidos
    _probar(
        "Sala con tarifa base cero",
        lambda: ReservaSala("SAL-B1", "Sala Cero", 0, capacidad_maxima=10),
    )
    _probar(
        "Equipo con stock negativo",
        lambda: AlquilerEquipo("EQ-B1", "Laptop", 50000, stock_total=-2),
    )
    _probar(
        "Asesoría con complejidad inexistente",
        lambda: AsesoriaEspecializada("ASE-B1", "Consultoría", 80000, nivel_complejidad="EXTREMA"),
    )

    # 3. Excepción encadenada por exceso de capacidad en sala
    cliente_prueba = Cliente("CLI-TEST", "Carlos Ruiz", "carlos@empresa.com", "3109876543")
    sala_pequena = ReservaSala(
        "SAL-TEST", "Sala Pequeña", 40000, capacidad_maxima=5, tiene_audiovisual=False
    )
    sistema.registrar_cliente(cliente_prueba)
    sistema.registrar_servicio(sala_pequena)

    def _crear_reserva_exceso_cupo():
        try:
            sistema.crear_reserva(
                id_reserva="RES-EXCESO",
                id_cliente="CLI-TEST",
                id_servicio="SAL-TEST",
                unidades=2,
                cantidad=12,
            )
        except ReservaInvalidaError as exc:
            assert isinstance(exc.__cause__, ServicioNoDisponibleError), (
                "Se esperaba ServicioNoDisponibleError encadenada en __cause__"
            )
            raise

    _probar("Encadenamiento ReservaInvalidaError <- ServicioNoDisponibleError", _crear_reserva_exceso_cupo)

    # 4. Transición de estado inválida en reserva (cancelar dos veces)
    reserva_valida = sistema.crear_reserva(
        id_reserva="RES-VALIDA-B",
        id_cliente="CLI-TEST",
        id_servicio="SAL-TEST",
        unidades=1,
        cantidad=3,
    )
    sistema.confirmar_reserva("RES-VALIDA-B")
    sistema.cancelar_reserva("RES-VALIDA-B")
    _probar(
        "Cancelar una reserva ya cancelada",
        lambda: sistema.cancelar_reserva("RES-VALIDA-B"),
    )
    _probar(
        "Confirmar una reserva ya cancelada",
        lambda: reserva_valida.confirmar(),
    )

    sistema._SistemaSoftwareFJ__logs.registrar_evento(
        "INFO", f"Pruebas de bordes ejecutadas: {len(resultados)} casos evaluados."
    )
    return resultados


#Parte 13: SIMULACIÓN INTEGRAL DE OPERACIONES (10+ CASOS VÁLIDOS E INVÁLIDOS)

def ejecutar_simulacion_integral() -> SistemaSoftwareFJ:
    #Ejecuta una simulación integral con más de 10 operaciones válidas e inválidas
    #sobre clientes, servicios y reservas en memoria, registrando todo en logs.
    gestor_logs = GestorLogs(carpeta="logs", nombre_archivo="software_fj.log")
    sistema = SistemaSoftwareFJ(gestor_logs=gestor_logs)

    print("\n--- INICIANDO SIMULACIÓN INTEGRAL (SOFTWARE FJ) ---")

    # Operación 1 [VÁLIDA]: Registrar clientes
    c1 = sistema.registrar_cliente(
        Cliente("CLI-01", "Laura Méndez", "laura.mendez@empresa.com", "3014567890")
    )
    c2 = sistema.registrar_cliente(
        Cliente("CLI-02", "Andrés Gómez", "andres.gomez@correo.org", "3157890123")
    )
    print(f"[OK 1] Clientes registrados: {c1.nombre}, {c2.nombre}")

    # Operación 2 [INVÁLIDA]: Registrar cliente con ID duplicado
    try:
        sistema.registrar_cliente(
            Cliente("CLI-01", "Laura Duplicada", "dup@empresa.com", "3014567890")
        )
    except SoftwareFJError as exc:
        print(f"[ERR 2 esperado] {exc}")

    # Operación 3 [INVÁLIDA]: Registrar cliente con correo inválido
    try:
        sistema.registrar_cliente(
            Cliente("CLI-03", "Pedro Inválido", "pedro_sin_dominio", "3201112233")
        )
    except SoftwareFJError as exc:
        print(f"[ERR 3 esperado] {exc}")

    # Operación 4 [VÁLIDA]: Registrar servicios especializados (Sala, Equipo, Asesoría)
    sala_auditorio = sistema.registrar_servicio(
        ReservaSala(
            id_servicio="SRV-SALA-1",
            nombre="Sala Conferencias Norte",
            tarifa_base=120000,
            capacidad_maxima=30,
            tiene_audiovisual=True,
            recargo_audiovisual=0.15,
        )
    )
    equipo_laptops = sistema.registrar_servicio(
        AlquilerEquipo(
            id_servicio="SRV-EQ-1",
            nombre="Estación Portátil Ingeniería",
            tarifa_base=45000,
            stock_total=6,
            costo_seguro_unidad=8000,
        )
    )
    asesoria_arq = sistema.registrar_servicio(
        AsesoriaEspecializada(
            id_servicio="SRV-ASE-1",
            nombre="Arquitectura de Sistemas y POO",
            tarifa_base=150000,
            nivel_complejidad="AVANZADA",
            recargo_urgencia=0.25,
            cupo_maximo_sesiones=5,
        )
    )
    print(
        f"[OK 4] Servicios registrados: {sala_auditorio.id_entidad}, "
        f"{equipo_laptops.id_entidad}, {asesoria_arq.id_entidad}"
    )

    # Operación 5 [VÁLIDA]: Crear y confirmar reserva de sala con audiovisual y descuento
    res1 = sistema.crear_reserva(
        id_reserva="RES-01",
        id_cliente="CLI-01",
        id_servicio="SRV-SALA-1",
        unidades=3,
        cantidad=20,
        incluir_audiovisual=True,
        descuento_porcentaje=10,
    )
    sistema.confirmar_reserva("RES-01")
    print(f"[OK 5] {res1.obtener_resumen()}")

    # Operación 6 [VÁLIDA]: Crear y confirmar alquiler de equipos (descuenta stock)
    res2 = sistema.crear_reserva(
        id_reserva="RES-02",
        id_cliente="CLI-02",
        id_servicio="SRV-EQ-1",
        unidades=2,
        cantidad=4,
        cantidad_equipos=4,
    )
    sistema.confirmar_reserva("RES-02")
    print(
        f"[OK 6] {res2.obtener_resumen()} | Stock restante laptops: {equipo_laptops.stock_disponible}"
    )

    # Operación 7 [VÁLIDA]: Crear y confirmar asesoría especializada urgente
    res3 = sistema.crear_reserva(
        id_reserva="RES-03",
        id_cliente="CLI-01",
        id_servicio="SRV-ASE-1",
        unidades=2,
        cantidad=1,
        urgente=True,
    )
    sistema.confirmar_reserva("RES-03")
    print(f"[OK 7] {res3.obtener_resumen()}")

    # Operación 8 [INVÁLIDA]: Intentar reservar más equipos que el stock disponible (quedan 2)
    try:
        sistema.crear_reserva(
            id_reserva="RES-04",
            id_cliente="CLI-02",
            id_servicio="SRV-EQ-1",
            unidades=1,
            cantidad=5,
            cantidad_equipos=5,
        )
    except SoftwareFJError as exc:
        print(f"[ERR 8 esperado] {exc}")

    # Operación 9 [VÁLIDA]: Cancelar reserva confirmada de equipos y verificar liberación de stock
    sistema.cancelar_reserva("RES-02")
    print(
        f"[OK 9] Reserva RES-02 cancelada ({res2.estado}) | "
        f"Stock liberado laptops: {equipo_laptops.stock_disponible}"
    )

    # Operación 10 [INVÁLIDA]: Intentar confirmar una reserva ya cancelada
    try:
        sistema.confirmar_reserva("RES-02")
    except SoftwareFJError as exc:
        print(f"[ERR 10 esperado] {exc}")

    # Operación 11 [INVÁLIDA]: Crear reserva con cliente inexistente
    try:
        sistema.crear_reserva(
            id_reserva="RES-05",
            id_cliente="CLI-999",
            id_servicio="SRV-SALA-1",
            unidades=1,
            cantidad=5,
        )
    except SoftwareFJError as exc:
        print(f"[ERR 11 esperado] {exc}")

    # Operación 12 [VÁLIDA]: Ejecutar batería de pruebas de bordes y excepciones encadenadas
    pruebas = ejecutar_pruebas_bordes(sistema)
    exitosas = sum(1 for p in pruebas if p["estado"] == "OK")
    print(f"[OK 12] Pruebas de bordes completadas: {exitosas}/{len(pruebas)} exitosas")

    return sistema


#Parte 14: AUDITORÍA FINAL DE LOGS Y PUNTO DE ENTRADA DEL SISTEMA

def auditar_archivo_logs(sistema: SistemaSoftwareFJ) -> dict[str, int]:
    #Audita el archivo de logs generado durante la ejecución y contabiliza
    #los registros por nivel (INFO, WARN, ERROR).
    resumen_niveles: dict[str, int] = {"INFO": 0, "WARN": 0, "ERROR": 0, "OTROS": 0}
    gestor_logs = sistema._SistemaSoftwareFJ__logs
    ruta_log = gestor_logs._GestorLogs__ruta_archivo

    print("\n--- AUDITORÍA FINAL DEL ARCHIVO DE LOGS ---")
    if not os.path.exists(ruta_log):
        print(f"No se encontró el archivo de log en: {ruta_log}")
        return resumen_niveles

    archivo = None
    try:
        archivo = open(ruta_log, mode="r", encoding="utf-8")
        lineas = archivo.readlines()

        for linea in lineas:
            if "[INFO]" in linea:
                resumen_niveles["INFO"] += 1
            elif "[WARN]" in linea:
                resumen_niveles["WARN"] += 1
            elif "[ERROR]" in linea:
                resumen_niveles["ERROR"] += 1
            else:
                resumen_niveles["OTROS"] += 1

        print(f"Archivo auditado: {ruta_log} | Total de líneas: {len(lineas)}")
        print(
            f"Conteo -> INFO: {resumen_niveles['INFO']} | "
            f"WARN: {resumen_niveles['WARN']} | "
            f"ERROR: {resumen_niveles['ERROR']}"
        )
        gestor_logs.registrar_evento(
            "INFO",
            f"Auditoría final completada ({len(lineas)} líneas; "
            f"ERROR={resumen_niveles['ERROR']}, WARN={resumen_niveles['WARN']}).",
        )
    except OSError as exc:
        print(f"Error al auditar el archivo de logs '{ruta_log}': {exc}")
    finally:
        if archivo is not None and not archivo.closed:
            archivo.close()

    return resumen_niveles


if __name__ == "__main__":
    sistema_fj = ejecutar_simulacion_integral()
    print("\n" + sistema_fj.obtener_estado_general())
    auditar_archivo_logs(sistema_fj)