from translate import Translator

translator = Translator(from_lang='ru', to_lang='en')
trans = translator.translate("я крутой")
print(trans)
