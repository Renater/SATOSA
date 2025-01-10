from satosa.micro_services.base import ResponseMicroService
from satosa.response import Redirect

class AttributeCheck(ResponseMicroService):
    """
    A microservice that performs simple presence checks on response attributes.

    Example configuration:

      ```yaml
      config:
        mandatory_attributes:
            - sub
        redirect: http://error.domain.tld/services?errorType=missing_attributes&attributes={attributes}
      ```

    """

    def __init__(self, config, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.internal_attributes = kwargs["internal_attributes"]
        self.mandatory_attributes = config.get("mandatory_attributes", {})
        self.redirect_url = config.get("redirect_url", {})

    def process(self, context, data):
        """
        Manage consent and attribute filtering

        :type context: satosa.context.Context
        :type data: satosa.internal.InternalData
        :rtype: satosa.response.Response

        :param context: response context
        :param data: the response
        :return: response
        """
        missing_attributes = []
        for attribute in self.mandatory_attributes:
            values = data.attributes.get(attribute)
            if values is None:
                missing_attributes.append(self.internal_attributes["attributes"][attribute]["saml"])

        if missing_attributes:
            parameters = []
            for missing_attribute in missing_attributes:
                parameters.append("attributes[]={}".format(", ".join(missing_attribute)))

            if "?" in self.redirect_url:
                # query string already present
                url = self.redirect_url + "&" + "&".join(parameters)
            else:
                # no query string
                url = self.redirect_url + "?" + "&".join(parameters)

            return Redirect(url)
        else:
            return super().process(context, data)
