class ChatParameter:
    def __init__(self, chat_id, message):
        self.chat_id = chat_id
        self.message = message

class Action:
    def __init__(self, parameter):
        self.parameter = parameter
        self.output = None
    def execute(self):
        return self
    def get_output(self):
        return self.output
    def do_nothing(self, *args):
        pass

class Keyword:
    def __init__(self, keyword, synonyms=[]):
        self.keyword = keyword
        self.synonyms = synonyms

class Dialog:
    def __init__(self, actions=[]):
        self.actions = actions

class TextReceiverParameter:
    def __init__(self, allowed_keywords):
        self.allowed_keywords = allowed_keywords
        self.received_message = ''

    def set_received_message(self, received_message):
        self.received_message = received_message

class TextReceiver(Action):
    def execute(self):
        self.output = None
        for keyword in self.parameter.allowed_keywords:
            if self.parameter.received_message == keyword.keyword:
                self.output = keyword
                return self
            for synonym in keyword.synonyms:
                if self.parameter.received_message == keyword.synonyms:
                    self.output = keyword
                    return self
        return self

class SendTextParameter:
    def __init__(self, message, generate_response_parameter=None, generate_response_function=None):
        self.message = message
        self.generate_response_parameter = generate_response_parameter
        self.generate_response_function = generate_response_function

class SendText(Action):
    def execute(self):
        if self.parameter.generate_response_function != None:
            self.parameter.message = self.parameter.generate_response_function(self.parameter.generate_response_parameter)
        return self
    pass

class GoToDialogParameter:
    def __init__(self, dialog):
        self.dialog = dialog

class GoToDialog(Action):
    # no execution
    pass

class BranchingParameter:
    def __init__(self, condition_function, condition_parameter, output_if_true, output_if_false):
        self.condition_function = condition_function
        self.condition_parameter = condition_parameter
        self.output_if_true = output_if_true
        self.output_if_false = output_if_false

class Branching(Action):
    def execute(self):
        self.output = self.parameter.output_if_true if self.parameter.condition_function(self.parameter.condition_parameter) else self.parameter.output_if_false
        return self

class ScriptParameter:
    def __init__(self, function):
        self.function = function
        self.function_parameter = None

class Script(Action):
    def execute(self):
        self.output = self.parameter.function(self.parameter.function_parameter)
        return self

KEYWORD_HALO = Keyword('halo', ['hai', 'p'])
KEYWORD_1 = Keyword('1', [])
KEYWORD_2 = Keyword('2', [])
KEYWORD_3 = Keyword('3', [])
KEYWORD_4 = Keyword('4', [])
KEYWORD_SELESAI = Keyword('selesai', [])
KEYWORD_BATAL = Keyword('batal', [])

PECEL_SAYUR = 'Pecel sayur'
GADO_GADO = 'Gado-gado'
KAREDOK = 'Karedok'
KETOPRAK = 'Ketoprak'

makanan = [
    PECEL_SAYUR,
    GADO_GADO,
    KAREDOK,
    KETOPRAK,
]

map_keyword_to_makanan = {
    KEYWORD_1: makanan[0],
    KEYWORD_2: makanan[1],
    KEYWORD_3: makanan[2],
    KEYWORD_4: makanan[3],
}

pesanan = {}

def add_pesanan(parameter):
    # parameter 0: chat_parameter
    # parameter 1: keyword
    if parameter[0].chat_id not in pesanan.keys():
        pesanan[parameter[0].chat_id] = {}
        for m in makanan:
            pesanan[parameter[0].chat_id][m] = 0
    
    pesanan[parameter[0].chat_id][map_keyword_to_makanan[parameter[1]]] += 1

def get_menu():
    res = 'Menu:\n'
    for i in range(len(makanan)):
        res += '%d. %s\n' % (i + 1, makanan[i])
    return res

def get_current_pesanan(parameter):
    # parameter: chat_parameter
    if parameter.chat_id not in pesanan.keys():
        return 'Belum ada pesanan dari kamu, silakan pilih dari menu di atas. Ketik "selesai" jika sudah selesai, dan "batal" untuk membatalkan pesanan'

    res = 'Pesanan saat ini:\n'
    for m in makanan:
        if pesanan[parameter.chat_id][m] > 0:
            res += '  %d %s\n' % (pesanan[parameter.chat_id][m], m)
    return res

dialog_halo = Dialog([])
dialog_greeting = Dialog([])
dialog_pesan = Dialog([])
dialog_exit_tanpa_pesanan = Dialog([])
dialog_exit_dengan_pesanan = Dialog([])
dialog_add_pesanan = Dialog([])

dialog_halo.actions.append(
    TextReceiver(TextReceiverParameter([KEYWORD_HALO]))
)
dialog_halo.actions.append(
    GoToDialog(
        GoToDialogParameter(
            dialog_greeting
        )
    )
)

dialog_greeting.actions.append(
    SendText(
        SendTextParameter('Selamat datang di Ruang Makan, ada yang bisa dibantu? Ketik 1 untuk memesan, ketik 2 untuk keluar.')
    )
)
dialog_greeting.actions.append(
    TextReceiver(TextReceiverParameter([KEYWORD_1, KEYWORD_2]))
)

dialog_greeting.actions.append(
    Branching(
        BranchingParameter(
            lambda x : x == KEYWORD_1,
            None, # the output of previous action
            GoToDialog(
                GoToDialogParameter(
                    dialog_pesan
                )
            ),
            Branching(
                BranchingParameter(
                    lambda x : x == KEYWORD_2,
                    None, # the output of previous action
                    GoToDialog(
                        GoToDialogParameter(
                            dialog_exit_tanpa_pesanan
                        )
                    ),
                    GoToDialog(
                        GoToDialogParameter(
                            dialog_greeting
                        )
                    ),
                ),
            ),
        )
    )
)

dialog_pesan.actions.append(
    SendText(
        SendTextParameter(get_menu())
    )
)
dialog_pesan.actions.append(
    SendText(
        SendTextParameter('test', generate_response_function=get_current_pesanan)
    )
)

dialog_pesan.actions.append(
    TextReceiver(TextReceiverParameter([KEYWORD_1, KEYWORD_2, KEYWORD_3, KEYWORD_4, KEYWORD_SELESAI, KEYWORD_BATAL]))
)

dialog_pesan.actions.append(
    Branching(
        BranchingParameter(
            lambda x : x in [KEYWORD_1, KEYWORD_2, KEYWORD_3, KEYWORD_4],
            None, # the output of previous action
            GoToDialog(
                GoToDialogParameter(
                    dialog_add_pesanan
                )
            ),
            Branching(
                BranchingParameter(
                    lambda x : x == KEYWORD_BATAL,
                    None, # the output of previous action
                    GoToDialog(
                        GoToDialogParameter(
                            dialog_exit_tanpa_pesanan
                        )
                    ),
                    Branching(
                        BranchingParameter(
                            lambda x : x == KEYWORD_SELESAI,
                            None, # the output of previous action
                            GoToDialog(
                                GoToDialogParameter(
                                    dialog_exit_dengan_pesanan,
                                )
                            ),
                            GoToDialog(
                                GoToDialogParameter(
                                    dialog_pesan,
                                )
                            ),
                        ),
                    ),
                ),
            ),
        )
    )
)

dialog_add_pesanan.actions.append(
    Script(
        ScriptParameter(
            add_pesanan
        )
    )
)
dialog_add_pesanan.actions.append(
    GoToDialog(
        GoToDialogParameter(
            dialog_pesan
        )
    )
)

dialog_exit_dengan_pesanan.actions.append(
    SendText(
        SendTextParameter('Baik, pesanan kamu sudah diterima! Silakan ketik halo lagi untuk memesan ya!')
    )
)

dialog_exit_tanpa_pesanan.actions.append(
    SendText(
        SendTextParameter('Baik, silakan ketik halo lagi untuk memesan ya!')
    )
)


DEFAULT_DIALOG = dialog_halo