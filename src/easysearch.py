import os
import re
import json
import datetime
import urllib.parse
import keypirinha as kp
import keypirinha_util as kpu

class EasySearch(kp.Plugin):
    SECTION_MAIN = 'main'

    SECTION_ENGINE = 'engines'

    SECTION_HISTORY = 'history'

    REGEX_INPUT = r'([a-zA-Z][a-zA-Z0-9]*)\s(.+)'

    REGEX_ENGINES = r'([a-zA-Z][a-zA-Z0-9_]*)\s(.+)'

    ITEM_EASYSEARCH = kp.ItemCategory.USER_BASE + 1

    ITEM_EASYSEARCH_HISTORY = kp.ItemCategory.USER_BASE + 2

    def __init__(self):
        super().__init__()
        self._debug = True

    def on_start(self):
        self._load_settings()
        self._gather_engines()

        self.history_file = os.path.join(
            self.get_package_cache_path(True),
            'history.json'
        )

        self.keep_history = self.settings.get_bool('keep_history', self.SECTION_HISTORY, False)
        self.history_keyword = self.settings.get_stripped('history_keyword', self.SECTION_HISTORY, 'esh')
        self.history_sort = self.settings.get_stripped('history_sort', self.SECTION_HISTORY, 'popular')

        self._set_actions()

    def on_catalog(self):
        self.on_start()

    def on_suggest(self, user_input, items_chain):
        input = re.search(self.REGEX_INPUT, user_input)

        if input is None or len(input.groups()) < 1:
            return None

        self.user_input = user_input

        if self.keep_history == True:
            if input.group(1) == self.history_keyword:
                history_suggestions = []

                with open(self.history_file, 'r+') as file:
                    try:
                        data = json.load(file)

                        if not data['data']:
                            data = self._get_boilerplate()
                    except Exception:
                        data = self._get_boilerplate()

                data = self._sort_by(self.history_sort, data['data'])

                for idx, entry in enumerate(data):
                    for engine in self.engines:
                        if engine == entry['engine']:
                            name = self._get_url_group(engine)[0].strip()
                            history_suggestions.append(
                                self._set_suggestion(
                                    self.ITEM_EASYSEARCH_HISTORY,
                                    self._create_label(self.history_keyword + ' ' + entry['engine'], name, entry['term']),
                                    entry['url']
                                )
                            )

                self.set_suggestions(history_suggestions, kp.Match.FUZZY, kp.Sort.TARGET_ASC)

        suggestions = []

        for engine in self.engines:
            if engine == input.group(1):
                url_group = self._get_url_group(engine)

                if len(url_group) == 2:
                    name, target = url_group
                    term = input.group(2)
                    target = target.strip().format(q = urllib.parse.quote(term).strip())

                    suggestions.append(
                        self._set_suggestion(
                            self.ITEM_EASYSEARCH,
                            self._create_label(engine, name, term),
                            target
                        )
                    )

                    split = target.split('://')

                    if split[0] == 'http':
                        target = 'https://' + split[1]

                        suggestions.append(
                            self._set_suggestion(
                                self.ITEM_EASYSEARCH,
                                self._create_label(engine, name, term),
                                target
                            )
                        )

                    self.set_suggestions(suggestions, kp.Match.FUZZY, kp.Sort.TARGET_ASC)

    def on_execute(self, item, action):
        if item.category() not in [self.ITEM_EASYSEARCH, self.ITEM_EASYSEARCH_HISTORY]:
            return

        private_mode = self.settings.get_bool('private_mode', self.SECTION_MAIN, False)
        new_window = self.settings.get_bool('new_window', self.SECTION_MAIN, False)

        if action and action.name() == "copy":
            kpu.set_clipboard(item.target())
        elif action and action.name() == "private":
            self._open_browser(item, True, new_window)
        elif action and action.name() == "new":
            self._open_browser(item, private_mode, True)
        elif action and action.name() == "delete":
            self._delete_entry(item)
        elif action and action.name() == "clear":
            self._clear_history()
        else:
            self._open_browser(item, private_mode, new_window)

    def on_events(self, flags):
        if flags & kp.Events.PACKCONFIG:
            self.on_start()

    def _open_browser(self, item, private_mode, new_window):
        kpu.web_browser_command(
            private_mode = private_mode,
            new_window = new_window,
            url = item.target(),
            execute = True
        )

        self._create_history(item)

    def _create_label(self, engine, name, term):
        return engine + ' : Search ' + name + ' for ' + term

    def _set_suggestion(self, category, label, target):
        return self.create_item(
            category = category,
            label = label,
            short_desc = target,
            target = target,
            args_hint = kp.ItemArgsHint.FORBIDDEN,
            hit_hint = kp.ItemHitHint.IGNORE,
            loop_on_suggest = True
        )

    def _set_error(self, msg):
        return [
            self.create_error_item(
                label = "Error",
                short_desc = msg,
                target = error
            )
        ]

    def _set_action(self, name, label, desc):
        return self.create_action(
            name = name,
            label = label,
            short_desc = desc
        )

    def _load_settings(self):
        self.settings = self.load_settings()

    def _gather_engines(self):
        self.engines = self.settings.keys(self.SECTION_ENGINE)

    def _save_json(self, data):
        with open(self.history_file, 'w') as outfile:
            json.dump(data, outfile)

    def _create_history(self, item):
        if self.keep_history != True:
            return None

        input = re.search(self.REGEX_INPUT, self.user_input)

        if input is None or len(input.groups()) != 2:
            return None

        self._create_history_file()

        with open(self.history_file, 'r+') as file:
            try:
                data = json.load(file)

                if not data['data']:
                    data = self._get_boilerplate()
            except Exception:
                data = self._get_boilerplate()

            for idx, entry in enumerate(data["data"]):
                if entry['url'] == item.target():
                    entry = self._update_history(file, data, entry)

                    return entry

            data = self._add_history(file, data, item, input)

    def _history_template(self, id, date, last_accessed, url, engine, term):
        return {
            "count": 1,
            "date": date,
            "engine": engine,
            "id": id,
            "last_accessed": last_accessed,
            "term": term,
            "url": url
        }

    def _get_date(self):
        return datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

    def _get_uuid(self):
        import uuid

        return uuid.uuid4().hex

    def _get_boilerplate(self):
        return {
            "name": self.package_full_name() + " Package",
            "data":[]
        }

    def _create_history_file(self):
        if not os.path.isfile(self.history_file):
            self._save_json(self._get_boilerplate())

    def _set_actions(self):
        main_actions = []

        main_actions.append(self._set_action('copy', 'Copy Link', 'Copy the URL to the clipboard'))
        main_actions.append(self._set_action('open', 'Open', 'Open the URL in the browser'))
        main_actions.append(self._set_action('new', 'New window', 'Open the URL in new browser window'))
        main_actions.append(self._set_action('private', 'Private mode', 'Open the URL in the private mode'))

        self.set_actions(
            self.ITEM_EASYSEARCH,
            main_actions
        )

        history_actions = []

        history_actions.append(self._set_action('copy', 'Copy Link', 'Copy the URL to the clipboard'))
        history_actions.append(self._set_action('open', 'Open', 'Open the URL in the browser'))
        history_actions.append(self._set_action('new', 'New window', 'Open the URL in new browser window'))
        history_actions.append(self._set_action('private', 'Private mode', 'Open the URL in the private mode'))
        history_actions.append(self._set_action('delete', 'Delete', 'Delete the current history entry'))
        history_actions.append(self._set_action('clear', 'Clear All', 'Clear the history'))

        self.set_actions(
            self.ITEM_EASYSEARCH_HISTORY,
            history_actions
        )

    def _get_url_group(self, setting):
        setting = self.settings.get_stripped(setting, self.SECTION_ENGINE)
        url = re.search(self.REGEX_ENGINES, setting)

        if len(url.groups()) == 2:
            name, target = url.groups()

            return [
                name.strip().replace("_", " "),
                target
            ]

    def _add_history(self, file, data, item, input):
        data["data"].insert(
            0,
            self._history_template(
                self._get_uuid(),
                self._get_date(),
                self._get_date(),
                item.target(),
                input.group(1),
                input.group(2)
            )
        )

        file.seek(0)
        json.dump(data, file, indent = 4)
        file.truncate()

        return data

    def _update_history(self, file, data, entry):
        entry['count'] += 1
        entry['last_accessed'] = self._get_date()

        file.seek(0)
        json.dump(data, file, indent = 4)
        file.truncate()

        return entry

    def _delete_entry(self, item):
        with open(self.history_file, 'r+') as file:
            try:
                content = json.load(file)

                if not content['data']:
                    content = self._get_boilerplate()
            except Exception:
                content = self._get_boilerplate()

            for idx, entry in enumerate(content['data']):
                if entry['url'] == item.target():
                    content['data'].pop(idx)

            file.seek(0)
            json.dump(content, file, indent = 4)
            file.truncate()

    def _clear_history(self):
        with open(self.history_file, 'r+') as file:
            file.seek(0)
            json.dump(self._get_boilerplate(), file, indent = 4)
            file.truncate()

    def _sort_by(self, algo, entries):
        reverse = False

        def count_sort(entry):
            return entry['count']

        def date_sort(entry):
            return datetime.datetime.strptime(entry['last_accessed'], "%Y-%m-%dT%H:%M:%S")

        if algo == 'popular':
            reverse = True
            algorithm = count_sort
        elif algo == 'unpopular':
            algorithm = count_sort
        elif algo == 'latest':
            algorithm = date_sort
            reverse = True
        elif algo == 'oldest':
            algorithm = date_sort

        return sorted(entries, key = algorithm, reverse = reverse)
