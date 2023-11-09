from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.gridlayout import GridLayout
from kivy.metrics import dp
from kivy.uix.scrollview import ScrollView
import json
import openai
import asynckivy as ak


# Lee el archivo JSON
with open('os.json', 'r') as clave_OPENai_json:
    datos = json.load(clave_OPENai_json)

# Extrae la clave privada del diccionario
OPENAI_API_KEY = datos['OPENAI_API_KEY']


class GymApp(BoxLayout):
    def __init__(self, **kwargs):
        super(GymApp, self).__init__(**kwargs)
        self.orientation = 'vertical'
        self.users = {}
        self.profiles = {}
        self.objetives = {}
        self.diets = {}
        self.routine = {} 
        self.weight_popup = None
        self.load_data_from_file()

        # Pantalla de inicio
        self.login_button = Button(text="Iniciar Sesión")
        self.register_button = Button(text="Registrarse")
        self.login_button.bind(on_press=self.show_login_popup)
        self.register_button.bind(on_press=self.show_register_popup)

        self.add_widget(self.login_button)
        self.add_widget(self.register_button)

    def show_login_popup(self, instance):
        content = BoxLayout(orientation='vertical')
        self.login_popup = Popup(title='Iniciar Sesión', content=content, size_hint=(None, None), size=(300, 200))

        username_label = Label(text='Usuario:')
        self.username_input = TextInput()
        password_label = Label(text='Contraseña:')
        self.password_input = TextInput(password=True)
        login_button = Button(text='Iniciar Sesión')
        login_button.bind(on_press=self.do_login)

        content.add_widget(username_label)
        content.add_widget(self.username_input)
        content.add_widget(password_label)
        content.add_widget(self.password_input)
        content.add_widget(login_button)

        self.login_popup.open()

    def do_login(self, instance):
        username = self.username_input.text
        password = self.password_input.text
        if self.login(username, password):
            self.login_popup.dismiss()
            self.user_profile = username
            self.show_main_screen()
        else:
            self.show_error_popup("Credenciales inválidas")

    def login(self, username, password):
        if username in self.users and self.users[username]["contrasena"] == password:
            self.user_profile = username
            return True
        return False

    def show_register_popup(self, instance):
        content = BoxLayout(orientation='vertical')
        self.register_popup = Popup(title='Registrarse', content=content, size_hint=(None, None), size=(300, 200))

        new_username_label = Label(text='Nuevo usuario:')
        self.new_username_input = TextInput()
        new_password_label = Label(text='Nueva contraseña:')
        self.new_password_input = TextInput(password=True)
        register_button = Button(text='Registrarse')
        register_button.bind(on_press=self.do_register)

        content.add_widget(new_username_label)
        content.add_widget(self.new_username_input)
        content.add_widget(new_password_label)
        content.add_widget(self.new_password_input)
        content.add_widget(register_button)

        self.register_popup.open()

    def do_register(self, instance):
        username = self.new_username_input.text
        password = self.new_password_input.text
        if self.register(username, password):
            self.register_popup.dismiss()
            self.user_profile = username
            self.register_profile()
            self.show_main_screen()
        else:
            self.show_error_popup("El usuario ya existe")

    def show_error_popup(self, message):
        content = BoxLayout(orientation='vertical')
        error_popup = Popup(title='Error', content=content, size_hint=(None, None), size=(300, 150))
        error_label = Label(text=message)
        ok_button = Button(text="OK")
        ok_button.bind(on_press=error_popup.dismiss)

        content.add_widget(error_label)
        content.add_widget(ok_button)

        error_popup.open()

    def register(self, username, password):
        if username not in self.users:
            new_user = {
                "usuario": username,
                "contrasena": password
            }
            self.users[username] = new_user
            self.save_data_to_file()
            return True
        return False

    def register_profile(self):
        content = GridLayout(cols=2, padding=10, spacing=10)
        profile_popup = Popup(title='Formulario de Registro de Perfil', content=content, size_hint=(None, None), size=(300, 200))

        weight_label = Label(text='Peso (kg):')
        height_label = Label(text='Altura (centímetros):')
        weight_input = TextInput()
        height_input = TextInput()

        register_button = Button(text='Registrar')
        register_button.bind(on_press=lambda instance: self.do_register_profile(weight_input.text, height_input.text, profile_popup))

        content.add_widget(weight_label)
        content.add_widget(weight_input)
        content.add_widget(height_label)
        content.add_widget(height_input)
        content.add_widget(register_button)

        profile_popup.open()

    def do_register_profile(self, weight, height, profile_popup):
        try:
            weight = float(weight)
            height = float(height)
            self.profiles[self.user_profile] = {
                "weight": weight,
                "height": height
            }
            self.save_data_to_file()
            profile_popup.dismiss()
            self.show_success_popup("Perfil registrado con éxito.")
        except ValueError:
            self.show_error_popup("Ingresa un peso y altura válidos")

    def show_success_popup(self, message):
        content = BoxLayout(orientation='vertical')
        success_popup = Popup(title='Éxito', content=content, size_hint=(None, None), size=(300, 200))
        success_label = Label(text=message)
        ok_button = Button(text="OK")
        ok_button.bind(on_press=success_popup.dismiss)

        content.add_widget(success_label)
        content.add_widget(ok_button)

        success_popup.open()

    def show_error_popup(self, message):
        content = BoxLayout(orientation='vertical')
        error_popup = Popup(title='Error', content=content, size_hint=(None, None), size=(300, 150))
        error_label = Label(text=message)
        ok_button = Button(text="OK")
        ok_button.bind(on_press=error_popup.dismiss)

        content.add_widget(error_label)
        content.add_widget(ok_button)

        error_popup.open()

    def save_data_to_file(self):
        data = {
            "users": self.users,
            "profiles": self.profiles,
            "objetives": self.objetives,
            "diets": self.diets,
            "routine": self.routine
        }
        with open("new_users.json", "w") as file:
            json.dump(data, file)

    def load_data_from_file(self):
        try:
            with open("new_users.json", "r") as file:
                data = json.load(file)
                self.users = data.get("users", {})
                self.profiles = data.get("profiles", {})
                self.objetives = data.get("objetives",{})
                self.diets = data.get("diets", {})
                self.routine = data.get("routine", {})
        except FileNotFoundError:
            self.users = {}
            self.profiles = {}
            self.objetives = {}
            self.diets = {}
            self.routine = {}

    def show_main_screen(self):
        self.clear_widgets()
        main_label = Label(text="Bienvenido a la Gym App")
        view_routine_button = Button(text="Ver Rutina de Ejercicios")
        view_diet_button = Button(text="Ver Plan de Dieta")
        create_routine_button = Button(text="Crear Rutina de Ejercicios")
        create_diet_button = Button(text="Crear Plan de Dieta")
        adjust_weight_button = Button(text="Ajustar Peso")
        logout_button = Button(text="Cerrar Sesión")

        view_routine_button.bind(on_press=self.view_routine)
        view_diet_button.bind(on_press=self.view_diet)
        create_routine_button.bind(on_press=self.create_routine_interface)
        #create_diet_button.bind(on_press=self.create_diet)
        #create_diet_button.bind(on_press=lambda instance: self.create_diet())
        #create_diet_button.bind(on_press=lambda instance: asyncio.ensure_future(self.create_diet()))
        create_diet_button.bind(on_press=self.create_diet_interface)



        adjust_weight_button.bind(on_press=self.adjust_weight)
        logout_button.bind(on_press=self.logout)

        self.add_widget(main_label)
        self.add_widget(view_routine_button)
        self.add_widget(view_diet_button)
        self.add_widget(create_routine_button)
        self.add_widget(create_diet_button)
        self.add_widget(adjust_weight_button)
        self.add_widget(logout_button)

    def adjust_weight(self, instance):
        if self.user_profile in self.profiles:
            content = BoxLayout(orientation='vertical')
            self.weight_popup = Popup(title='Ajustar Peso', content=content, size_hint=(None, None), size=(300, 200))

            weight_label = Label(text='Ingresa tu peso actual (kg):')
            self.weight_input = TextInput()
            save_button = Button(text='Guardar Peso')

            save_button.bind(on_press=self.save_weight)

            content.add_widget(weight_label)
            content.add_widget(self.weight_input)
            content.add_widget(save_button)

            self.weight_popup.open()

    def save_weight(self, instance):
        try:
            current_weight = float(self.weight_input.text)
            previous_weight = self.profiles[self.user_profile].get("weight", current_weight)
            weight_change = previous_weight - current_weight
            self.profiles[self.user_profile]["weight"] = current_weight
            self.save_data_to_file()
            message = (f"Peso anterior: {previous_weight:.2f} kg\n"
                       f"Peso actual: {current_weight:.2f} kg\n")
            if weight_change > 0:
                message += f"Has bajado {abs(weight_change):.2f} kg"
            elif weight_change < 0:
                message += f"Has subido {abs(weight_change):.2f} kg"
            else:
                message += "Tu peso se ha mantenido igual."
            self.show_success_popup(message)
            self.weight_popup.dismiss()
        except ValueError:
            self.show_error_popup("Por favor, ingresa un peso válido.")



    async def generate_openai_response(self,pregunta_dieta):
        openai.api_key = OPENAI_API_KEY
        print(openai.api_key)
        print("Creando dieta, espere un momento...")
        print(pregunta_dieta)

        print(self.user_profile)
        #print(self.routine[self.user_profile])

        promt = '"\\nPlan de dieta:\\n" \
                "Día 1:\\n" \
                "\\n| Comida       | Alimentos                                 | Calorías |\\n" \
                "|--------------|-------------------------------------------|----------|\\n" \
                "| Desayuno     | 2 huevos cocidos, 1 rebanada de pan integral | 220 kcal |\\n" \
                "| Almuerzo     | Pollo a la parrilla, ensalada de espinacas   | 310 kcal |\\n" \
                "| Cena         | Salmón a la parrilla, brócoli al vapor       | 285 kcal |\\n" \
                "| Merienda     | Yogur natural bajo en grasa, frutas         | 127 kcal |\\n"'
        
        print(promt)
    
        response = await ak.run_in_thread(lambda: openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{
                "role": "system",
                "content": "You are a helpful gym assistant."
            }, {
                "role": "user",
                "content":f"{promt} con los siguientes objetivos {pregunta_dieta}"
                }],
            max_tokens=100)
        )

        print(f"{response.choices[0].message['content'].strip()}")

        Openai_recommended_diet = response.choices[0].message['content'].strip()

        #try:
        #    with open("new_users.json", "r") as file:
        #        data = json.load(file)
        #        data[self.diets][self.user_profile] = {
        #            "Dieta recomendada": Openai_recommended_diet,
        #            "Estado": "OK"
        #    }

        #        data[self.objetives][self.users]=""
        #        data[self.diets][self.users]=""



        #except FileNotFoundError:
        #    self.users = {}
        #    self.profiles = {}
        #    self.objetives = {}
        #    self.diets = {}

        print(self.user_profile)
        #self.diets[self.user_profile]['Dieta recomendada'] = Openai_recommended_diet

        self.diets[self.user_profile] = {
            "Dieta recomendada" : Openai_recommended_diet,
            "Estado" : "OK"
        }
        self.save_data_to_file()

        self.objetive_popup.dismiss()
        self.show_success_popup("¡Dieta creada con éxito!")

        #return response.choices[0].message['content'].strip()


    # Vamos a crear la dieta

    def create_diet_interface(self, instance):
        

        content = BoxLayout(orientation='vertical')
        self.objetive_popup = Popup(title='Objetivo de peso', content=content, size_hint=(None, None), size=(400, 300))
        goal_label = Label(text="¿Cuál es tu objetivo? (perder grasa, volumen, mantenimiento): ")
        self.goal_input = TextInput()
        save_button = Button(text='Guardar Objetivo')
        

        #No puede guardarse la dieta y verla sin haberla creado antes. Es necesario esperar la respuesta de ChatGPT
        #save_button.bind(on_press=self.view_diet)

        save_button.bind(on_press=self.create_diet)
        
        content.add_widget(goal_label)
        content.add_widget(self.goal_input)
        content.add_widget(save_button)

        self.objetive_popup.open()
    

    def create_diet(self, instance):

        weight = self.profiles.get(self.user_profile, {}).get("weight", 0)

        protein_ratio = 2.0 if self.goal_input.text == "volumen" else 2.0 if self.goal_input.text == "mantenimiento" else 2.5
        protein = weight * protein_ratio
        fat = weight * 0.3
        carbs = 4 * (protein + fat)

        self.objetives[self.user_profile] = {
            "goal": self.goal_input.text,
            "protein": protein,
            "fat": fat,
            "carbs": carbs
        }

        self.save_data_to_file()
        
        ak.start(self.generate_openai_response(self.objetives[self.user_profile]))


    def view_diet(self,instance):
        if self.user_profile in self.diets:
            diet_info = self.diets[self.user_profile]['Dieta recomendada']

            self.show_success_popup_2("Plan de Dieta", diet_info)
        else:
            self.show_error_popup("No tienes una dieta creada.")


    def show_diet_success_popup(self, message, diet):
        
        content = BoxLayout(orientation='vertical')
        success_popup = Popup(title=message, content=content, size_hint=(None, None), size=(600, 500))
        success_label = Label(text=diet.strip())
        ok_button = Button(text="OK")
        ok_button.bind(on_press=success_popup.dismiss)

        content.add_widget(success_label)
        content.add_widget(ok_button)

        success_popup.open()

    def show_success_popup_2(self,message,json_info):
        # Crea un Popup con tamaño automático basado en el contenido
        popup = Popup(title=message, size_hint=(None, None), size=(400, 300))

        # Crea un ScrollView
        scroll_view = ScrollView()

        # Contenido del ScrollView
        content_label = Label(text=str(json_info), text_size=(None, None), height=dp(10))
        content_label.bind(size=content_label.setter('text_size'))

        # Agrega el Label al ScrollView
        scroll_view.add_widget(content_label)

        # Contenido del Popup
        layout = BoxLayout(orientation='vertical')
        layout.add_widget(scroll_view)

        # Asigna el contenido al Popup
        popup.content = layout

        # Abre el Popup
        popup.open()











    async def generate_openai_response_routine(self,pregunta_rutina):
        openai.api_key = OPENAI_API_KEY
        #print(openai.api_key)
        print("Creando rutina, espere un momento...")
        print(pregunta_rutina)

        promt = """
            Por favor, crea una rutina de ejercicios para mí. Mi objetivo es mejorar mi condición física general y aumentar mi resistencia. 
            Me gustaría incluir ejercicios para el cardio, la fuerza y la flexibilidad. Preferiría una rutina que pueda realizar en casa sin equipo especializado.

            Día 1:
            - Calentamiento: 10 minutos de saltos de cuerda.
            - Cardio: 30 minutos de jogging en el lugar.
            - Fuerza: 3 series de 15 repeticiones de sentadillas y flexiones.
            - Flexibilidad: 10 minutos de estiramientos de cuerpo completo.

            Resto de días...
            """
        
        print(promt)
    
        response = await ak.run_in_thread(lambda: openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{
                "role": "system",
                "content": "You are a helpful gym coach assistant."
            }, {
                "role": "user",
                "content":f"{promt} durante los siguientes {pregunta_rutina} días"
                }],
            max_tokens=100)
        )

        #print(f"{response.choices[0].message['content'].strip()}")

        Openai_recommended_routine = response.choices[0].message['content'].strip()


        print("\n\n\n\n")

        print(Openai_recommended_routine)

        print("\n\n\n\n")
        
        self.routine[self.user_profile] = {
            "Rutina recomendada" : Openai_recommended_routine,
            "Estado" : "OK"
        }
        

        #self.diets[self.user_profile]['Dieta recomendada'] 

        self.save_data_to_file()
        self.objetive_popup.dismiss()
        self.show_success_popup("¡Rutina creada con éxito!")









    def create_routine_interface(self, instance):
        content = BoxLayout(orientation='vertical')
        self.objetive_popup = Popup(title='Rutina', content=content, size_hint=(None, None), size=(400, 300))
        days_label = Label(text="¿Cuantos días quieres de entrenamiento?: ")
        self.days_input = TextInput()
        save_button = Button(text='Guardar Objetivo')
        

        #No puede guardarse la dieta y verla sin haberla creado antes. Es necesario esperar la respuesta de ChatGPT
        #save_button.bind(on_press=self.view_diet)

        save_button.bind(on_press=self.create_routine)
        
        content.add_widget(days_label)
        content.add_widget(self.days_input)
        content.add_widget(save_button)

        self.objetive_popup.open()


    def create_routine(self, instance):      
        
        self.save_data_to_file()
        ak.start(self.generate_openai_response_routine(self.days_input))












    def view_routine(self,instance):
        if self.user_profile in self.routine:
            routine_info = self.routine[self.user_profile]['Rutina recomendada']

            self.show_success_popup_2("Rutina de entrenamiento", routine_info)
        else:
            self.show_error_popup("No tienes una rutina creada.")



    def logout(self, instance):
        self.user_profile = None
        self.clear_widgets()
        self.show_login_screen()

    def show_login_screen(self):
        self.add_widget(self.login_button)
        self.add_widget(self.register_button)







class GymAppMain(App):
    def build(self):
        return GymApp()

if __name__ == "__main__":
    app = GymAppMain()
    app.run()
