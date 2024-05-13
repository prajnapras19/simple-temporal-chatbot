from transitions import Machine

class ChatParameter:
    def __init__(self, chat_id, message):
        self.chat_id = chat_id
        self.message = message

class ChatbotFSM:
    initial_state = 'intention_checking'
    states = ['intention_checking', 'promo_category_list', 'promo_weekend_list', 'promo_weekdays_list', 'no_action_ending']#, 'order_addition', 'promo_code_usage', 'order_ending']
    transitions = [
        {
            'trigger': 'get_promo',
            'source': 'intention_checking',
            'dest': 'promo_category_list',
            'after': 'reply_get_promo',
        },
        {
            'trigger': 'get_promo_weekend',
            'source': 'promo_category_list',
            'dest': 'promo_weekend_list',
            'before': 'reply_get_promo_weekend',
        },
        {
            'trigger': 'get_promo_weekdays',
            'source': 'promo_category_list',
            'dest': 'promo_weekdays_list',
            'before': 'reply_get_promo_weekdays',
        },
        {
            'trigger': 'back',
            'source': 'promo_weekend_list',
            'dest': 'intention_checking',
            'before': 'reply_intention_checking',
        },
        {
            'trigger': 'back',
            'source': 'promo_weekdays_list',
            'dest': 'intention_checking',
            'before': 'reply_intention_checking',
        },
        {
            'trigger': 'end',
            'source': 'intention_checking',
            'dest': 'no_action_ending',
            'before': 'reply_no_action_ending',
            'after': 'complete_chat'
        },   
    ]

    def __init__(self, chat_parameter):
        self.is_completed = False
        
        self.chat_parameter = chat_parameter
        self.unrecognized_option_reply = 'Perintah tidak dikenali.'
        
        self.reply = 'Selamat datang di Ruang Makan, ada yang bisa dibantu? Ketik "get_promo" untuk melihat promo, ketik "end" untuk keluar.'
        self.machine = Machine(model=self, states=ChatbotFSM.states, transitions=ChatbotFSM.transitions, initial=ChatbotFSM.initial_state)

    def complete_chat(self):
        self.is_completed = True

    def reply_get_promo(self):
        self.reply = 'Promo apa yang kamu ingin lihat? Ketik "get_promo_weekdays" atau "get_promo_weekend".'
    
    def reply_get_promo_weekdays(self):
        self.reply = 'Ada promo weekdays nih: beli 2 gratis 2. Ketik "back" untuk kembali ke menu.'
    
    def reply_get_promo_weekend(self):
        self.reply = 'Ada promo weekend nih: beli 3 gratis 3. Ketik "back" untuk kembali ke menu.'
    
    def reply_intention_checking(self):
        self.reply = 'Ketik get_promo untuk melihat promo, ketik end untuk keluar.'
    
    def reply_no_action_ending(self):
        self.reply = 'sampai jumpa'