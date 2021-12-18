import json


class MyObject:
    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)

    @staticmethod
    def float_to_string(value: float):
        text = str(value)
        texts = text.split('e')
        print(texts)
        if len(texts) < 2:
            return str(value)
        else:
            if int(texts[1]) < 0:
                result = '0.' + '0' * abs(int(texts[1]) + 1) + texts[0].replace('.', '')
            else:
                result = texts[0].replace('.', '') + '0' * abs(int(texts[1]))

            return result
