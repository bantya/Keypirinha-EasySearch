import re
import keypirinha as kp
import keypirinha_util as kpu

class EasySearch(kp.Plugin):
    SECTION_ENGINE = 'engines'

    SECTION_MAIN = 'main'

    REGEX_INPUT = r'(\S+)\s(.+)'

    REGEX_ENGINES = r'(\S+)\s(.+)'

    ITEM_CAT = kp.ItemCategory.USER_BASE + 1

    def __init__(self):
        super().__init__()

    def on_start(self):
        self._load_settings()
        self._gather_engines()

    def on_catalog(self):
        self.on_start()

    def on_suggest(self, user_input, items_chain):
        input = re.search(self.REGEX_INPUT, user_input)

        if input is None:
            return None

        for engine in self.engines:
            if engine == input.group(1):
                setting = self.settings.get_stripped(engine, section = self.SECTION_ENGINE, fallback = '')
                url = re.search(self.REGEX_ENGINES, setting)

                if len(url.groups()) == 2:
                    name, target = url.groups()
                    term = input.group(2)
                    name = name.strip().replace("_", " ")
                    target = target.strip().format(q=term.strip())

                    suggestion = self._set_suggestion(name, target)
                    self.set_suggestions(suggestion, kp.Match.FUZZY, kp.Sort.TARGET_ASC)

    def _set_suggestion(self, name, target):
        return [
            self.create_item(
                category = self.ITEM_CAT,
                label = name + ' : ' + target,
                short_desc = target,
                target = target,
                args_hint = kp.ItemArgsHint.FORBIDDEN,
                hit_hint = kp.ItemHitHint.IGNORE,
                loop_on_suggest = True
            )
        ]

    def _set_error(self, msg):
        return [
            self.create_error_item(
                label = "Error",
                short_desc = msg,
                target = error
            )
        ]

    def on_execute(self, item, action):
        if item.category() != self.ITEM_CAT:
            return

        kpu.web_browser_command(
            private_mode = self.settings.get_bool('private_mode', section = self.SECTION_MAIN, fallback = False),
            new_window = self.settings.get_bool('new_window', section = self.SECTION_MAIN, fallback = False),
            url = item.target(),
            execute = True
        )

    def _load_settings(self):
        self.settings = self.load_settings()

    def _gather_engines(self):
        self.engines = self.settings.keys(self.SECTION_ENGINE)

    def on_events(self, flags):
        if flags & kp.Events.PACKCONFIG:
            self.on_start()
