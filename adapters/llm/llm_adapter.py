from abc import ABC, abstractmethod

class LLMAdapter(ABC):
    @abstractmethod
    def generate_response(self, prompt: str, **kwargs) -> str:
        """
        Verilen prompt'a göre LLM'den yanıt üretir.
        :param prompt: LLM'ye gönderilecek metin prompt'u.
        :param kwargs: Model parametreleri (temperature, max_tokens, vs.).
        :return: LLM'den gelen yanıt metni.
        """
        pass

    @abstractmethod
    def get_model_info(self) -> dict:
        """
        Kullanılan LLM modeli hakkında bilgi döndürür.
        :return: Model bilgileri (isim, kapasite, vs.).
        """
        pass

    @abstractmethod
    def stream_response(self, prompt: str, **kwargs):
        """
        LLM'den yanıtı akış halinde (stream) üretir.
        :param prompt: LLM'ye gönderilecek metin prompt'u.
        :param kwargs: Model parametreleri (temperature, max_tokens, vs.).
        :return: Akış halindeki yanıtı üreten bir jeneratör.
        """
        pass

    @abstractmethod
    def chat_completion(self, messages: list[dict], **kwargs) -> str:
        """
        Sohbet geçmişine dayalı LLM'den yanıt üretir.
        :param messages: Sohbet geçmişi (örn. [{"role": "user", "content": "Hi"}]).
        :param kwargs: Model parametreleri (temperature, max_tokens, vs.).
        :return: LLM'den gelen yanıt metni.
        """
        pass
