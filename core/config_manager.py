import os
import xml.etree.ElementTree as ET
from xml.dom import minidom


class ConfigManager:
    """
    负责加载、保存和管理WinSW的XML配置。
    """
    # 将logpath移到SIMPLE_TAGS中，作为顶级元素处理
    SIMPLE_TAGS = [
        'id', 'name', 'description', 'executable', 'arguments',
        'workingdirectory', 'resetfailure', 'priority', 'stoptimeout',
        'logpath'
    ]

    def get_default_config(self) -> dict:
        """返回一个新服务的默认配置字典。"""
        config = {tag: '' for tag in self.SIMPLE_TAGS}
        config['log_mode'] = 'roll'  # 将默认模式改为更常用的roll
        # logpath 默认值为空字符串，由mainwindow在保存时处理
        config['onfailure'] = []
        config['resetfailure'] = '1 day'
        config['priority'] = 'normal'
        config['stoptimeout'] = '15 sec'
        config['interactive'] = False
        config['serviceaccount'] = {}
        config['environments'] = []
        return config

    def _from_xml_root(self, root) -> dict:
        """从一个XML Element根节点解析配置到字典。"""
        config = self.get_default_config()
        # SIMPLE_TAGS现在包含了logpath，会自动被正确加载
        for tag in self.SIMPLE_TAGS:
            element = root.find(tag)
            if element is not None and element.text is not None:
                config[tag] = element.text.strip()

        config['interactive'] = root.find('interactive') is not None

        # log标签只处理mode属性
        log_element = root.find('log')
        if log_element is not None:
            config['log_mode'] = log_element.get('mode', 'append')

        config['onfailure'] = [{'action': el.get('action', ''), 'delay': el.get('delay', '')} for el in
                               root.findall('onfailure')]

        config['environments'] = [{'name': el.get('name', ''), 'value': el.get('value', '')} for el in
                                  root.findall('env')]

        sa_element = root.find('serviceaccount')
        if sa_element is not None:
            username_el, password_el, allow_logon_el = sa_element.find('username'), sa_element.find(
                'password'), sa_element.find('allowservicelogon')
            config['serviceaccount'] = {
                'username': username_el.text.strip() if username_el is not None and username_el.text else '',
                'password': password_el.text.strip() if password_el is not None and password_el.text else '',
                'allowservicelogon': allow_logon_el is not None and allow_logon_el.text.lower() == 'true'
            }
        return config

    def load_from_xml(self, file_path: str) -> dict:
        """从XML文件加载配置。"""
        try:
            tree = ET.parse(file_path)
            return self._from_xml_root(tree.getroot())
        except (ET.ParseError, FileNotFoundError) as e:
            print(f"错误: 处理XML文件 {file_path} 时出错: {e}")
            return self.get_default_config()

    def load_from_xml_string(self, xml_string: str) -> dict:
        """从XML字符串加载配置。"""
        root = ET.fromstring(xml_string)
        return self._from_xml_root(root)

    def _to_xml_root(self, config: dict) -> ET.Element:
        """将配置字典转换为一个XML Element根节点。"""
        root = ET.Element("service")

        # 定义一个推荐的元素顺序
        ordered_tags = [
            'id', 'name', 'description', 'executable', 'arguments', 'workingdirectory'
        ]
        for tag in ordered_tags:
            if config.get(tag): ET.SubElement(root, tag).text = config[tag]

        if config.get('environments'):
            for env in config['environments']:
                if env.get('name'): ET.SubElement(root, 'env', attrib=env)

        # --- 关键修正处 ---
        # 1. logpath现在作为顶级元素处理
        # 2. log只处理mode属性
        # 3. 将所有剩余的简单标签（包括logpath）添加到XML中
        remaining_simple_tags = [tag for tag in self.SIMPLE_TAGS if tag not in ordered_tags]
        for tag in remaining_simple_tags:
            if config.get(tag): ET.SubElement(root, tag).text = config[tag]

        if config.get('interactive'): ET.SubElement(root, 'interactive').text = 'true'

        # 只生成带mode属性的log标签，不再包含子元素
        if config.get('log_mode'):
            ET.SubElement(root, 'log', attrib={'mode': config.get('log_mode')})
        # --- 修正结束 ---

        if config.get('onfailure'):
            for action_item in config['onfailure']:
                action = action_item.get('action')
                if not action: continue
                attribs = {'action': action}
                delay = action_item.get('delay')
                if delay: attribs['delay'] = delay
                ET.SubElement(root, 'onfailure', attrib=attribs)

        sa_config = config.get('serviceaccount')
        if sa_config and sa_config.get('username'):
            sa_element = ET.SubElement(root, 'serviceaccount')
            ET.SubElement(sa_element, 'username').text = sa_config['username']
            if sa_config.get('password'): ET.SubElement(sa_element, 'password').text = sa_config['password']
            if sa_config.get('allowservicelogon'): ET.SubElement(sa_element, 'allowservicelogon').text = 'true'

        return root

    def save_to_xml_string(self, config: dict) -> str:
        """将配置字典转换为格式化的XML字符串。"""
        root = self._to_xml_root(config)
        xml_string = ET.tostring(root, 'utf-8')
        parsed_string = minidom.parseString(xml_string)
        # 移除空行
        return os.linesep.join([s for s in parsed_string.toprettyxml(indent="  ").splitlines() if s.strip()])

    def save_to_xml(self, config: dict, file_path: str):
        """将配置字典保存为XML文件。"""
        pretty_xml = self.save_to_xml_string(config)
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(pretty_xml)
        except IOError as e:
            print(f"错误: 无法写入文件 {file_path}: {e}")
