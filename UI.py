import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QComboBox, QPushButton, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem, QScrollArea, QAbstractItemView, QTabWidget, QInputDialog, QTextEdit, QFormLayout
from PyQt5.QtCore import Qt
from backend import *


class PersonWindow(QWidget):
    def __init__(self, group):
        super().__init__()
        self.group = group
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Person Manager')
        self.setGeometry(100, 100, 800, 400)

        layout = QHBoxLayout()

        # Sidebar
        sidebar_layout = QVBoxLayout()

        # Search input
        search_label = QLabel('Search:')
        self.search_input = QLineEdit()
        self.search_input.textChanged.connect(self.filter_person_list)
        sidebar_layout.addWidget(search_label)
        sidebar_layout.addWidget(self.search_input)

        # Person list
        self.person_list = QListWidget()
        self.person_list.setSelectionMode(QAbstractItemView.SingleSelection)
        self.person_list.itemSelectionChanged.connect(self.show_person_details)
        sidebar_layout.addWidget(self.person_list)

        layout.addLayout(sidebar_layout)

        # Tab widget
        self.tab_widget = QTabWidget()
        self.tab_widget.addTab(PersonCreationTab(self), 'Create Person')
        self.tab_widget.addTab(PersonEditTab(self), 'Edit Person')
        layout.addWidget(self.tab_widget)

        self.setLayout(layout)
        self.update_person_list()

    def update_person_list(self):
        self.person_list.clear()
        for person_name in self.group.people.keys():
            item = QListWidgetItem(person_name)
            self.person_list.addItem(item)

    def filter_person_list(self, text):
        for row in range(self.person_list.count()):
            item = self.person_list.item(row)
            item.setHidden(text.lower() not in item.text().lower())

    def show_person_details(self):
        selected_items = self.person_list.selectedItems()
        if selected_items:
            person_name = selected_items[0].text()
            self.tab_widget.setCurrentIndex(1)
            self.tab_widget.widget(1).show_person_details(person_name)
            self.tab_widget.widget(1).update_relationship_list()


class PersonCreationTab(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.custom_attribute_layout = QVBoxLayout()
        self.custom_attribute_widgets = []
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Name input
        name_label = QLabel('<h2>Name:</h2>')
        self.name_input = QLineEdit()
        layout.addWidget(name_label)
        layout.addWidget(self.name_input)

        # Bio input
        bio_label = QLabel('<h4>Bio:</h4>')
        self.bio_input = QTextEdit()
        self.bio_input.setFixedHeight(100)
        layout.addWidget(bio_label)
        layout.addWidget(self.bio_input)

        # Email input
        email_layout = QHBoxLayout()
        email_label = QLabel('<h4>Email:</h4>')
        self.email_input = QLineEdit()
        email_layout.addWidget(email_label)
        email_layout.addWidget(self.email_input)
        layout.addLayout(email_layout)

        # Personal link input
        link_layout = QHBoxLayout()
        link_label = QLabel('<h4>Personal link:</h4>')
        self.link_input = QLineEdit()
        link_layout.addWidget(link_label)
        link_layout.addWidget(self.link_input)
        layout.addLayout(link_layout)

        # Custom attribute button
        custom_button = QPushButton('Add Custom Attribute')
        custom_button.clicked.connect(self.add_custom_attribute)
        layout.addWidget(custom_button)

        # Custom attribute layout
        layout.addLayout(self.custom_attribute_layout)

        # Create person button
        create_button = QPushButton('Create Person')
        create_button.clicked.connect(self.create_person)
        layout.addWidget(create_button)

        self.setLayout(layout)
        self.setFocusPolicy(Qt.StrongFocus)
        self.setFocus()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            self.create_person()
        else:
            super().keyPressEvent(event)

    def add_custom_attribute(self):
        attribute_widget = QWidget()
        attribute_layout = QHBoxLayout(attribute_widget)
        label_input = QLineEdit()
        content_input = QLineEdit()
        delete_button = QPushButton('-')
        delete_button.clicked.connect(lambda: self.delete_custom_attribute(attribute_widget))
        attribute_layout.addWidget(QLabel('Custom attribute label:'))
        attribute_layout.addWidget(label_input)
        attribute_layout.addWidget(QLabel('Custom attribute content:'))
        attribute_layout.addWidget(content_input)
        attribute_layout.addWidget(delete_button)
        self.custom_attribute_layout.addWidget(attribute_widget)
        self.custom_attribute_widgets.append(attribute_widget)

    def delete_custom_attribute(self, attribute_widget):
        self.custom_attribute_layout.removeWidget(attribute_widget)
        attribute_widget.deleteLater()
        self.custom_attribute_widgets.remove(attribute_widget)

    def create_person(self):
        name = self.name_input.text()
        bio = self.bio_input.toPlainText()
        email = self.email_input.text()
        link = self.link_input.text()

        if name:
            person = Person(name, self.parent.group)
            if bio:
                person.bio = bio
            if email:
                person.email = email
            if link:
                person.link = link

            for attribute_widget in self.custom_attribute_widgets:
                attribute_layout = attribute_widget.layout()
                label_input = attribute_layout.itemAt(1).widget()
                content_input = attribute_layout.itemAt(3).widget()
                if isinstance(label_input, QLineEdit) and isinstance(content_input, QLineEdit):
                    attr_name = label_input.text()
                    attr_value = content_input.text()
                    if attr_name and attr_value:
                        setattr(person, attr_name, attr_value)

            self.name_input.clear()
            self.bio_input.clear()
            self.email_input.clear()
            self.link_input.clear()
            self.clear_custom_attributes()
            self.parent.update_person_list()

    def clear_custom_attributes(self):
        for attribute_widget in self.custom_attribute_widgets:
            self.custom_attribute_layout.removeWidget(attribute_widget)
            attribute_widget.deleteLater()
        self.custom_attribute_widgets.clear()


class PersonEditTab(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Person name
        self.person_name_label = QLabel()
        self.person_name_label.setStyleSheet("font-weight: bold; font-size: 16px;")
        layout.addWidget(self.person_name_label)

        # Attribute layout
        self.attribute_layout = QFormLayout()
        layout.addLayout(self.attribute_layout)

        # Relationship list
        self.relationship_layout = QVBoxLayout()
        layout.addLayout(self.relationship_layout)

        # Relationship input
        relationship_layout = QHBoxLayout()
        self.relationship_input = QLineEdit()
        self.relationship_input.textChanged.connect(self.filter_person_list)
        relationship_layout.addWidget(self.relationship_input)

        # Relationship type dropdown
        self.relationship_type = QComboBox()
        self.relationship_type.addItem('Friends')
        self.relationship_type.addItem('Children')
        self.relationship_type.addItem('Partner')
        self.relationship_type.addItem('Coworkers/Colleagues')
        self.relationship_type.addItem('Custom')
        self.relationship_type.currentTextChanged.connect(self.handle_relationship_type)
        relationship_layout.addWidget(self.relationship_type)

        # Custom relationship input
        self.custom_relationship_input = QLineEdit()
        self.custom_relationship_input.setVisible(False)
        relationship_layout.addWidget(self.custom_relationship_input)

        # Add relationship button
        add_relationship_button = QPushButton('Add Relationship')
        add_relationship_button.clicked.connect(self.add_relationship)
        relationship_layout.addWidget(add_relationship_button)

        layout.addLayout(relationship_layout)

        self.setLayout(layout)

    def show_person_details(self, person_name):
        self.person = self.parent.group.people[person_name]
        self.person_name_label.setText(self.person.fullname)
        self.update_attribute_layout()
        self.update_relationship_list()

    def update_attribute_layout(self):
        # Clear the attribute layout
        while self.attribute_layout.rowCount():
            self.attribute_layout.removeRow(0)

        # Add attribute labels and edit buttons
        for attr_name, attr_value in self.person.__dict__.items():
            if attr_name not in ['firstname', 'lastname', 'middle', 'fullname', 'group'] and attr_name not in self.person.group.relationships:
                attribute_label = QLabel(f"{attr_name.capitalize()}:")
                attribute_widget = QWidget()
                attribute_layout = QHBoxLayout(attribute_widget)
                attribute_value_label = QLabel(str(attr_value))
                edit_button = QPushButton('Edit')
                edit_button.clicked.connect(lambda checked, a=attr_name, w=attribute_widget: self.edit_attribute(a, w))
                delete_button = QPushButton('Delete')
                delete_button.clicked.connect(lambda checked, a=attr_name: self.delete_attribute(a))
                attribute_layout.addWidget(attribute_value_label)
                attribute_layout.addWidget(edit_button)
                attribute_layout.addWidget(delete_button)
                self.attribute_layout.addRow(attribute_label, attribute_widget)

    def edit_attribute(self, attr_name, attribute_widget):
        attribute_layout = attribute_widget.layout()
        attribute_value_label = attribute_layout.itemAt(0).widget()
        edit_button = attribute_layout.itemAt(1).widget()

        attribute_value = attribute_value_label.text()
        attribute_input = QLineEdit(attribute_value)
        save_button = QPushButton('Save')
        save_button.clicked.connect(lambda checked, a=attr_name, i=attribute_input, w=attribute_widget: self.save_attribute(a, i, w))
        attribute_layout.replaceWidget(attribute_value_label, attribute_input)
        attribute_layout.replaceWidget(edit_button, save_button)
        attribute_value_label.setParent(None)
        edit_button.setParent(None)
        attribute_input.setFocus()

    def save_attribute(self, attr_name, attribute_input, attribute_widget):
        attribute_layout = attribute_widget.layout()
        save_button = attribute_layout.itemAt(1).widget()

        attribute_value = attribute_input.text()
        setattr(self.person, attr_name, attribute_value)
        attribute_value_label = QLabel(attribute_value)
        edit_button = QPushButton('Edit')
        edit_button.clicked.connect(lambda checked, a=attr_name, w=attribute_widget: self.edit_attribute(a, w))
        attribute_layout.replaceWidget(attribute_input, attribute_value_label)
        attribute_layout.replaceWidget(save_button, edit_button)
        attribute_input.setParent(None)
        save_button.setParent(None)

    def delete_attribute(self, attr_name):
        delattr(self.person, attr_name)
        self.update_attribute_layout()

    def update_relationship_list(self):
        for i in reversed(range(self.relationship_layout.count())):
            relationship_widget = self.relationship_layout.itemAt(i).widget()
            self.relationship_layout.removeWidget(relationship_widget)
            relationship_widget.deleteLater()

        for relationship, people in self.person.get_relationships().items():
            for person_name in people:
                relationship_widget = QWidget()
                relationship_layout = QHBoxLayout(relationship_widget)
                relationship_label = QLabel(f"{person_name} ({relationship})")
                delete_button = QPushButton('Delete')
                delete_button.clicked.connect(lambda checked, r=relationship, p=person_name: self.delete_relationship(r, p))
                relationship_layout.addWidget(relationship_label)
                relationship_layout.addWidget(delete_button)
                self.relationship_layout.addWidget(relationship_widget)

    def filter_person_list(self, text):
        for row in range(self.parent.person_list.count()):
            item = self.parent.person_list.item(row)
            item.setHidden(text.lower() not in item.text().lower())

    def handle_relationship_type(self, text):
        if text == 'Custom':
            self.custom_relationship_input.setVisible(True)
        else:
            self.custom_relationship_input.setVisible(False)

    def add_relationship(self):
        target_name = self.relationship_input.text()
        relationship_type = self.relationship_type.currentText()

        if relationship_type == 'Custom':
            relationship = self.custom_relationship_input.text()
            if not relationship:
                return
        else:
            relationship = relationship_type.lower()

        if target_name:
            if relationship in ['friends', 'partner', 'coworkers/colleagues']:
                self.person.add_undirected_relationship(target_name, relationship)
            else:
                self.person.add_directed_relationship(target_name, relationship)
            self.relationship_input.clear()
            self.custom_relationship_input.clear()
            self.parent.group.update_relationship_graphs()
            self.update_relationship_list()
            self.parent.update_person_list()

    def delete_relationship(self, relationship, person_name):
        self.person.remove_relationship(person_name, relationship)
        self.parent.group.update_relationship_graphs()
        self.update_relationship_list()

from PyQt5.QtWidgets import QFileDialog

def main():
    app = QApplication(sys.argv)

    # Prompt the user to select a file to read from
    filefrom, _ = QFileDialog.getOpenFileName(None, "Select File to Read From", "", "JSON Files (*.json)")

    # Create the group and window
    group = Group(filefrom) if filefrom else Group()
    window = PersonWindow(group)
    window.show()

    # Run the application
    result = app.exec_()

    # Prompt the user to select a file to write to when the program is closed
    if result == 0:  # Check if the application exited normally
        fileto, _ = QFileDialog.getSaveFileName(None, "Select File to Write To", "", "JSON Files (*.json)")
        if fileto:
            group.save_group_to_file(fileto)

    sys.exit(result)

if __name__ == '__main__':
    main()