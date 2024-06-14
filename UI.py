import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QComboBox, QPushButton, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem, QScrollArea, QAbstractItemView, QTabWidget, QInputDialog, QTextEdit, QFormLayout, QFileDialog, QDialog, QDialogButtonBox, QMessageBox, QCheckBox, QSplitter, QGroupBox
from PyQt5.QtCore import Qt
import configparser
from backend import *


class PersonWindow(QWidget):
    def __init__(self, group):
        super().__init__()
        self.group = group
        self.last_loaded_file = None 
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Person Manager')
        self.setGeometry(100, 100, 800, 500)

        layout = QVBoxLayout()

        # Splitter
        splitter = QSplitter()

        # Sidebar
        sidebar_widget = QWidget()
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

        # Load and Save buttons
        load_button = QPushButton('Load')
        load_button.clicked.connect(self.load_group)
        save_button = QPushButton('Save')
        save_button.clicked.connect(self.save_group)
        button_layout = QHBoxLayout()
        button_layout.addWidget(load_button)
        button_layout.addWidget(save_button)
        sidebar_layout.addLayout(button_layout)

        sidebar_widget.setLayout(sidebar_layout)
        sidebar_widget.setMaximumWidth(250)  # Set the maximum width for the sidebar
        splitter.addWidget(sidebar_widget)

        # Tab widget
        self.tab_widget = QTabWidget()
        self.tab_widget.addTab(self.create_scrollable_tab(PersonCreationTab(self)), 'Create Person')
        self.tab_widget.addTab(self.create_scrollable_tab(PersonEditTab(self)), 'Edit Person')
        splitter.addWidget(self.tab_widget)

        layout.addWidget(splitter)
        self.setLayout(layout)
        self.update_person_list()

    def create_scrollable_tab(self, tab_widget):
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(tab_widget)
        return scroll_area

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
            edit_tab = self.tab_widget.widget(1)
            edit_widget = edit_tab.widget()
            edit_widget.show_person_details(person_name)
            edit_widget.update_relationship_list()

    def load_group(self):
        if self.last_loaded_file:
            reply = QMessageBox.question(self, 'Save Changes', 'Do you want to save your changes before loading a new file?',
                                        QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel, QMessageBox.Yes)

            if reply == QMessageBox.Yes:
                self.group.save_group_to_file(self.last_loaded_file)

            if reply != QMessageBox.Cancel:
                file_name, _ = QFileDialog.getOpenFileName(self, "Open Group File", "", "JSON Files (*.json)")
                if file_name:
                    self.group = Group(file_name)
                    self.last_loaded_file = file_name
                    self.update_person_list()
        else:
            file_name, _ = QFileDialog.getOpenFileName(self, "Open Group File", "", "JSON Files (*.json)")
            if file_name:
                self.group = Group(file_name)
                self.last_loaded_file = file_name
                self.update_person_list()

    def save_group(self):
        file_name, _ = QFileDialog.getSaveFileName(self, "Save Group File", "", "JSON Files (*.json)")
        if file_name:
            self.group.save_group_to_file(file_name)
    
    def closeEvent(self, event):
        reply = QMessageBox.question(self, 'Save Changes', 'Do you want to save your changes?',
                                    QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel, QMessageBox.Yes)

        if reply == QMessageBox.Yes:
            if self.last_loaded_file:
                file_name = self.last_loaded_file
            else:
                file_name, _ = QFileDialog.getSaveFileName(self, "Save Group File", "", "JSON Files (*.json)")

            if file_name:
                self.group.save_group_to_file(file_name)
                event.accept()
            else:
                event.ignore()
        elif reply == QMessageBox.No:
            event.accept()
        else:
            event.ignore()


class PersonCreationTab(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.email_layout = QVBoxLayout()
        self.link_layout = QVBoxLayout()
        self.custom_attribute_layout = QVBoxLayout()
        self.relationship_list = QVBoxLayout()  # Add this line
        self.relationships = []
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Name input
        name_box = QGroupBox()
        name_layout = QVBoxLayout()
        name_label = QLabel('<h2>Name</h2>')
        self.name_input = QLineEdit()
        name_layout.addWidget(name_label)
        name_layout.addWidget(self.name_input)
        name_box.setLayout(name_layout)
        layout.addWidget(name_box)

        # Bio input
        bio_box = QGroupBox()
        bio_layout = QVBoxLayout()
        bio_label = QLabel('<h4>Bio</h4>')
        self.bio_input = QTextEdit()
        self.bio_input.setFixedHeight(100)
        bio_layout.addWidget(bio_label)
        bio_layout.addWidget(self.bio_input)
        bio_box.setLayout(bio_layout)
        layout.addWidget(bio_box)

        # Email section
        email_box = QGroupBox()
        email_layout = QVBoxLayout()
        self.email_title = QLabel('<h4>Emails</h4>')
        self.email_title.setVisible(False)
        email_layout.addWidget(self.email_title)
        email_layout.addLayout(self.email_layout)
        email_button = QPushButton('Add Email')
        email_button.clicked.connect(self.add_email)
        email_layout.addWidget(email_button)
        email_box.setLayout(email_layout)
        layout.addWidget(email_box)

        # Link section
        link_box = QGroupBox()
        link_layout = QVBoxLayout()
        self.link_title = QLabel('<h4>Personal Links</h4>')
        self.link_title.setVisible(False)
        link_layout.addWidget(self.link_title)
        link_layout.addLayout(self.link_layout)
        link_button = QPushButton('Add Personal Link')
        link_button.clicked.connect(self.add_link)
        link_layout.addWidget(link_button)
        link_box.setLayout(link_layout)
        layout.addWidget(link_box)

        # Custom attribute section
        custom_attribute_box = QGroupBox()
        custom_attribute_layout = QVBoxLayout()
        self.custom_attribute_title = QLabel('<h4>Custom Attributes</h4>')
        self.custom_attribute_title.setVisible(False)
        custom_attribute_layout.addWidget(self.custom_attribute_title)
        custom_attribute_layout.addLayout(self.custom_attribute_layout)
        custom_button = QPushButton('Add Custom Attribute')
        custom_button.clicked.connect(self.add_custom_attribute)
        custom_attribute_layout.addWidget(custom_button)
        custom_attribute_box.setLayout(custom_attribute_layout)
        layout.addWidget(custom_attribute_box)

        # Relationship section
        relationship_box = QGroupBox()
        relationship_layout = QVBoxLayout()
        relationship_list_title = QLabel('<h4>Relationships</h4>')
        relationship_layout.addWidget(relationship_list_title)
        relationship_layout.addLayout(self.relationship_list)
        relationship_input_layout = QHBoxLayout()
        relationship_input_label = QLabel("Name:")
        relationship_input_layout.addWidget(relationship_input_label)
        self.relationship_input = QLineEdit()
        self.relationship_input.textChanged.connect(self.update_suggestions)
        relationship_input_layout.addWidget(self.relationship_input)
        relationship_layout.addLayout(relationship_input_layout)
        self.suggestion_list = QListWidget()  # Add this line
        self.suggestion_list.setVisible(False)  # Add this line
        self.suggestion_list.itemClicked.connect(self.autofill_relationship)  # Add this line
        relationship_layout.addWidget(self.suggestion_list)
        relationship_type_layout = QHBoxLayout()
        self.relationship_type = QComboBox()
        self.relationship_type.addItem('Friends')
        self.relationship_type.addItem('Children')
        self.relationship_type.addItem('Partner')
        self.relationship_type.addItem('Coworkers/Colleagues')
        self.relationship_type.addItem('Custom')
        self.relationship_type.currentTextChanged.connect(self.handle_relationship_type)
        relationship_type_layout.addWidget(self.relationship_type)
        self.custom_relationship_input = QLineEdit()
        self.custom_relationship_input.setVisible(False)
        relationship_type_layout.addWidget(self.custom_relationship_input)
        self.directed_checkbox = QCheckBox("Directed")
        self.directed_checkbox.setVisible(False)
        relationship_type_layout.addWidget(self.directed_checkbox)
        add_relationship_button = QPushButton('Add Relationship')
        add_relationship_button.clicked.connect(self.add_relationship)
        relationship_type_layout.addWidget(add_relationship_button)
        relationship_layout.addLayout(relationship_type_layout)
        relationship_box.setLayout(relationship_layout)
        layout.addWidget(relationship_box)

        # Create person button
        create_button = QPushButton('Create Person')
        create_button.clicked.connect(self.create_person)
        layout.addWidget(create_button)

        self.setLayout(layout)
        self.setFocusPolicy(Qt.StrongFocus)
        self.setFocus()

    def add_email(self):
        email_widget = QWidget()
        email_layout = QHBoxLayout(email_widget)
        email_input = QLineEdit()
        delete_button = QPushButton('-')
        delete_button.clicked.connect(lambda: self.delete_email(email_widget))
        email_layout.addWidget(email_input)
        email_layout.addWidget(delete_button)
        self.email_layout.addWidget(email_widget)
        self.email_title.setVisible(True)

    def delete_email(self, email_widget):
        self.email_layout.removeWidget(email_widget)
        email_widget.deleteLater()
        if not self.email_layout.count():
            self.email_title.setVisible(False)

    def add_link(self):
        link_widget = QWidget()
        link_layout = QHBoxLayout(link_widget)
        link_input = QLineEdit()
        delete_button = QPushButton('-')
        delete_button.clicked.connect(lambda: self.delete_link(link_widget))
        link_layout.addWidget(link_input)
        link_layout.addWidget(delete_button)
        self.link_layout.addWidget(link_widget)
        self.link_title.setVisible(True)

    def delete_link(self, link_widget):
        self.link_layout.removeWidget(link_widget)
        link_widget.deleteLater()
        if not self.link_layout.count():
            self.link_title.setVisible(False)

    def add_custom_attribute(self):
        attribute_widget = QWidget()
        attribute_layout = QHBoxLayout(attribute_widget)
        label_input = QLineEdit()
        content_input = QLineEdit()
        delete_button = QPushButton('-')
        delete_button.clicked.connect(lambda: self.delete_custom_attribute(attribute_widget))
        attribute_layout.addWidget(QLabel('Label:'))
        attribute_layout.addWidget(label_input)
        attribute_layout.addWidget(QLabel('Content:'))
        attribute_layout.addWidget(content_input)
        attribute_layout.addWidget(delete_button)
        self.custom_attribute_layout.addWidget(attribute_widget)
        self.custom_attribute_title.setVisible(True)

    def delete_custom_attribute(self, attribute_widget):
        self.custom_attribute_layout.removeWidget(attribute_widget)
        attribute_widget.deleteLater()

    def create_person(self):
        name = self.name_input.text()
        bio = self.bio_input.toPlainText()

        if name:
            person = Person(name, self.parent.group)
            self.person = person
            if bio:
                person.bio = bio

            for i in range(self.email_layout.count()):
                email_input = self.email_layout.itemAt(i).widget()
                if isinstance(email_input, QLineEdit):
                    email = email_input.text()
                    if email:
                        person.emails.append(email)

            for i in range(self.link_layout.count()):
                link_input = self.link_layout.itemAt(i).widget()
                if isinstance(link_input, QLineEdit):
                    link = link_input.text()
                    if link:
                        person.links.append(link)

            for i in range(self.custom_attribute_layout.count()):
                attribute_widget = self.custom_attribute_layout.itemAt(i).widget()
                attribute_layout = attribute_widget.layout()
                label_input = attribute_layout.itemAt(1).widget()
                content_input = attribute_layout.itemAt(3).widget()
                if isinstance(label_input, QLineEdit) and isinstance(content_input, QLineEdit):
                    attr_name = label_input.text()
                    attr_value = content_input.text()
                    if attr_name and attr_value:
                        if not hasattr(person, 'custom_attributes'):
                            person.custom_attributes = {}
                        person.custom_attributes[attr_name] = attr_value
            
            for target_name, relationship, directed in self.relationships:
                if directed:
                    person.add_directed_relationship(target_name, relationship)
                else:
                    person.add_undirected_relationship(target_name, relationship)

            self.name_input.clear()
            self.bio_input.clear()
            self.clear_emails()
            self.clear_links()
            self.clear_custom_attributes()
            self.email_title.setVisible(False)
            self.link_title.setVisible(False)
            self.custom_attribute_title.setVisible(False)
            self.relationships.clear()
            self.parent.update_person_list()
            self.parent.person_list.setCurrentRow(self.parent.person_list.count() - 1)

    def clear_emails(self):
        while self.email_layout.count():
            email_input = self.email_layout.takeAt(0).widget()
            email_input.deleteLater()

    def clear_links(self):
        while self.link_layout.count():
            link_input = self.link_layout.takeAt(0).widget()
            link_input.deleteLater()

    def clear_custom_attributes(self):
        while self.custom_attribute_layout.count():
            attribute_widget = self.custom_attribute_layout.takeAt(0).widget()
            attribute_widget.deleteLater()
    
    def update_suggestions(self, text):
        self.suggestion_list.clear()
        if text:
            suggestions = [person for person in self.parent.group.people if text.lower() in person.lower()]
            self.suggestion_list.addItems(suggestions)
            self.suggestion_list.setVisible(True)
        else:
            self.suggestion_list.setVisible(False)

    def autofill_relationship(self, item):
        self.relationship_input.setText(item.text())
        self.suggestion_list.setVisible(False)

    def handle_relationship_type(self, text):
        if text == 'Custom':
            self.custom_relationship_input.setVisible(True)
            self.directed_checkbox.setVisible(True)
        else:
            self.custom_relationship_input.setVisible(False)
            self.directed_checkbox.setVisible(False)
    
    def update_relationship_list(self):
        for i in reversed(range(self.relationship_list.count())):
            relationship_widget = self.relationship_list.itemAt(i).widget()
            self.relationship_list.removeWidget(relationship_widget)
            relationship_widget.deleteLater()

        for target_name, relationship, directed in self.relationships:
            relationship_widget = QWidget()
            relationship_layout = QHBoxLayout(relationship_widget)
            relationship_label = QLabel(f"{target_name} ({relationship})")
            delete_button = QPushButton('Delete')
            delete_button.clicked.connect(lambda _, t=target_name, r=relationship, d=directed: self.delete_relationship(t, r, d))
            relationship_layout.addWidget(relationship_label)
            relationship_layout.addWidget(delete_button)
            self.relationship_list.addWidget(relationship_widget)

    def add_relationship(self):
        target_name = self.relationship_input.text()
        relationship_type = self.relationship_type.currentText()

        if relationship_type == 'Custom':
            relationship = self.custom_relationship_input.text()
            if not relationship:
                return
            directed = self.directed_checkbox.isChecked()
        else:
            relationship = relationship_type.lower()
            directed = relationship not in ['friend', 'partner', 'coworker/colleague']

        if target_name:
            self.relationships.append((target_name, relationship, directed))
            self.relationship_input.clear()
            self.custom_relationship_input.clear()
            self.suggestion_list.setVisible(False)
            self.update_relationship_list()

    def delete_relationship(self, target_name, relationship, directed):
        self.relationships.remove((target_name, relationship, directed))
        self.update_relationship_list()


class PersonEditTab(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.email_layout = QVBoxLayout()  # Add this line
        self.link_layout = QVBoxLayout()  # Add this line
        self.custom_attribute_layout = QVBoxLayout()  # Add this line
        self.relationship_layout = QVBoxLayout()  # Add this line
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Person name
        person_name_box = QGroupBox()
        person_name_layout = QVBoxLayout()
        self.person_name_label = QLabel()
        self.person_name_label.setStyleSheet("font-weight: bold; font-size: 16px;")
        person_name_layout.addWidget(self.person_name_label)
        person_name_box.setLayout(person_name_layout)
        layout.addWidget(person_name_box)

        # Bio section
        bio_box = QGroupBox()
        bio_layout = QVBoxLayout()
        self.bio_label = QLabel('<h4>Bio</h4>')
        self.bio_label.setVisible(False)
        self.bio_text = QLabel()
        self.bio_text.setWordWrap(True)
        self.bio_button = QPushButton('Add Bio')
        self.bio_button.clicked.connect(self.edit_bio)
        bio_layout.addWidget(self.bio_label)
        bio_layout.addWidget(self.bio_text)
        bio_layout.addWidget(self.bio_button)
        bio_box.setLayout(bio_layout)
        layout.addWidget(bio_box)

        # Email section
        email_box = QGroupBox()
        email_layout = QVBoxLayout()
        self.email_title = QLabel('<h4>Emails</h4>')  # Add this line
        self.email_title.setVisible(False)  # Add this line
        email_layout.addWidget(self.email_title)
        email_layout.addLayout(self.email_layout)
        add_email_button = QPushButton('Add Email')
        add_email_button.clicked.connect(self.add_email)
        email_layout.addWidget(add_email_button)
        email_box.setLayout(email_layout)
        layout.addWidget(email_box)

        # Link section
        link_box = QGroupBox()
        link_layout = QVBoxLayout()
        self.link_title = QLabel('<h4>Personal Links</h4>')  # Add this line
        self.link_title.setVisible(False)  # Add this line
        link_layout.addWidget(self.link_title)
        link_layout.addLayout(self.link_layout)
        add_link_button = QPushButton('Add Personal Link')
        add_link_button.clicked.connect(self.add_link)
        link_layout.addWidget(add_link_button)
        link_box.setLayout(link_layout)
        layout.addWidget(link_box)

        # Custom attribute section
        custom_attribute_box = QGroupBox()
        custom_attribute_layout = QVBoxLayout()
        self.custom_attribute_title = QLabel('<h4>Custom Attributes</h4>')  # Add this line
        self.custom_attribute_title.setVisible(False)  # Add this line
        custom_attribute_layout.addWidget(self.custom_attribute_title)
        custom_attribute_layout.addLayout(self.custom_attribute_layout)
        add_custom_attribute_button = QPushButton('Add Custom Attribute')
        add_custom_attribute_button.clicked.connect(self.add_custom_attribute)
        custom_attribute_layout.addWidget(add_custom_attribute_button)
        custom_attribute_box.setLayout(custom_attribute_layout)
        layout.addWidget(custom_attribute_box)

        # Relationship section
        relationship_box = QGroupBox()
        relationship_layout = QVBoxLayout()
        relationship_layout.addWidget(QLabel('<h4>Relationships</h4>'))
        relationship_layout.addLayout(self.relationship_layout)  # Update this line
        relationship_input_layout = QHBoxLayout()
        relationship_input_label = QLabel("Name:")
        relationship_input_layout.addWidget(relationship_input_label)
        self.relationship_input = QLineEdit()
        self.relationship_input.textChanged.connect(self.update_suggestions)
        relationship_input_layout.addWidget(self.relationship_input)
        relationship_layout.addLayout(relationship_input_layout)
        self.suggestion_list = QListWidget()  # Add this line
        self.suggestion_list.setVisible(False)  # Add this line
        self.suggestion_list.itemClicked.connect(self.autofill_relationship)  # Add this line
        relationship_layout.addWidget(self.suggestion_list)
        relationship_type_layout = QHBoxLayout()
        self.relationship_type = QComboBox()
        self.relationship_type.addItem('Friends')
        self.relationship_type.addItem('Children')
        self.relationship_type.addItem('Partner')
        self.relationship_type.addItem('Coworkers/Colleagues')
        self.relationship_type.addItem('Custom')
        self.relationship_type.currentTextChanged.connect(self.handle_relationship_type)
        relationship_type_layout.addWidget(self.relationship_type)
        self.custom_relationship_input = QLineEdit()
        self.custom_relationship_input.setVisible(False)
        relationship_type_layout.addWidget(self.custom_relationship_input)
        self.directed_checkbox = QCheckBox("Directed")
        self.directed_checkbox.setVisible(False)
        relationship_type_layout.addWidget(self.directed_checkbox)
        add_relationship_button = QPushButton('Add Relationship')
        add_relationship_button.clicked.connect(self.add_relationship)
        relationship_type_layout.addWidget(add_relationship_button)
        relationship_layout.addLayout(relationship_type_layout)
        relationship_box.setLayout(relationship_layout)
        layout.addWidget(relationship_box)

        # Delete Person button
        delete_person_button = QPushButton('Delete Person')
        delete_person_button.clicked.connect(self.delete_person)
        layout.addWidget(delete_person_button)

        self.setLayout(layout)

    def show_person_details(self, person_name):
        self.person = self.parent.group.people[person_name]
        self.person_name_label.setText(self.person.fullname)
        self.update_bio_display()
        self.update_email_layout()
        self.update_link_layout()
        self.update_custom_attribute_layout()
        self.update_relationship_list()

    def update_bio_display(self):
        if hasattr(self.person, 'bio') and self.person.bio:
            self.bio_label.setVisible(True)
            self.bio_text.setText(self.person.bio)
            self.bio_button.setText('Edit Bio')
        else:
            self.bio_label.setVisible(False)
            self.bio_text.clear()
            self.bio_button.setText('Add Bio')

    def edit_bio(self):
        bio_dialog = QDialog(self)
        bio_dialog.setWindowTitle('Edit Bio')
        layout = QVBoxLayout()
        self.bio_editor = QTextEdit()
        if hasattr(self.person, 'bio'):
            self.bio_editor.setText(self.person.bio)
        layout.addWidget(self.bio_editor)
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(bio_dialog.accept)
        button_box.rejected.connect(bio_dialog.reject)
        layout.addWidget(button_box)
        bio_dialog.setLayout(layout)
        if bio_dialog.exec() == QDialog.Accepted:
            bio = self.bio_editor.toPlainText()
            self.person.bio = bio
            self.update_bio_display()

    def update_email_layout(self):
        # Clear the email layout
        while self.email_layout.count():
            email_widget = self.email_layout.takeAt(0).widget()
            email_widget.deleteLater()

        if self.person.emails:
            self.email_title.setVisible(True)
            # Add email labels and edit/delete buttons
            for email in self.person.emails:
                email_widget = QWidget()
                email_layout = QHBoxLayout(email_widget)
                email_label = QLabel(email)
                edit_button = QPushButton('Edit')
                edit_button.clicked.connect(lambda checked, e=email, w=email_widget: self.edit_email(e, w))
                delete_button = QPushButton('Delete')
                delete_button.clicked.connect(lambda checked, e=email: self.delete_email(e))
                email_layout.addWidget(email_label)
                email_layout.addWidget(edit_button)
                email_layout.addWidget(delete_button)
                self.email_layout.addWidget(email_widget)
        else:
            self.email_title.setVisible(False)

    def update_link_layout(self):
        # Clear the link layout
        while self.link_layout.count():
            link_widget = self.link_layout.takeAt(0).widget()
            link_widget.deleteLater()

        if self.person.links:
            self.link_title.setVisible(True)
            # Add link labels and edit/delete buttons
            for link in self.person.links:
                link_widget = QWidget()
                link_layout = QHBoxLayout(link_widget)
                link_label = QLabel(link)
                edit_button = QPushButton('Edit')
                edit_button.clicked.connect(lambda checked, l=link, w=link_widget: self.edit_link(l, w))
                delete_button = QPushButton('Delete')
                delete_button.clicked.connect(lambda checked, l=link: self.delete_link(l))
                link_layout.addWidget(link_label)
                link_layout.addWidget(edit_button)
                link_layout.addWidget(delete_button)
                self.link_layout.addWidget(link_widget)
        else:
            self.link_title.setVisible(False)

    def update_custom_attribute_layout(self):
        # Clear the custom attribute layout
        while self.custom_attribute_layout.count():
            custom_attribute_widget = self.custom_attribute_layout.takeAt(0).widget()
            custom_attribute_widget.deleteLater()

        if hasattr(self.person, 'custom_attributes') and self.person.custom_attributes:
            self.custom_attribute_title.setVisible(True)
            # Add custom attribute labels and edit/delete buttons
            for attr_name, attr_value in self.person.custom_attributes.items():
                custom_attribute_widget = QWidget()
                custom_attribute_layout = QHBoxLayout(custom_attribute_widget)
                custom_attribute_label = QLabel(f"{attr_name}: {attr_value}")
                edit_button = QPushButton('Edit')
                edit_button.clicked.connect(lambda checked, n=attr_name, v=attr_value, w=custom_attribute_widget: self.edit_custom_attribute(n, v, w))
                delete_button = QPushButton('Delete')
                delete_button.clicked.connect(lambda checked, n=attr_name: self.delete_custom_attribute(n))
                custom_attribute_layout.addWidget(custom_attribute_label)
                custom_attribute_layout.addWidget(edit_button)
                custom_attribute_layout.addWidget(delete_button)
                self.custom_attribute_layout.addWidget(custom_attribute_widget)
        else:
            self.custom_attribute_title.setVisible(False)

    def add_email(self):
        email_input = QLineEdit()
        save_button = QPushButton('Save')
        save_button.clicked.connect(lambda checked, i=email_input: self.save_email(i))
        email_widget = QWidget()
        email_layout = QHBoxLayout(email_widget)
        email_layout.addWidget(email_input)
        email_layout.addWidget(save_button)
        self.email_layout.addWidget(email_widget)

    def save_email(self, email_input):
        email = email_input.text()
        if email:
            self.person.emails.append(email)
            self.update_email_layout()

    def edit_email(self, email, email_widget):
        email_layout = email_widget.layout()
        email_label = email_layout.itemAt(0).widget()
        edit_button = email_layout.itemAt(1).widget()
        email_input = QLineEdit(email)
        save_button = QPushButton('Save')
        save_button.clicked.connect(lambda checked, e=email, i=email_input, w=email_widget: self.save_edited_email(e, i, w))
        email_layout.replaceWidget(email_label, email_input)
        email_layout.replaceWidget(edit_button, save_button)
        email_label.setParent(None)
        edit_button.setParent(None)
        email_input.setFocus()

    def save_edited_email(self, old_email, email_input, email_widget):
        new_email = email_input.text()
        if new_email:
            self.person.emails.remove(old_email)
            self.person.emails.append(new_email)
            self.update_email_layout()

    def delete_email(self, email):
        self.person.emails.remove(email)
        self.update_email_layout()

    def add_link(self):
        link_input = QLineEdit()
        save_button = QPushButton('Save')
        save_button.clicked.connect(lambda checked, i=link_input: self.save_link(i))
        link_widget = QWidget()
        link_layout = QHBoxLayout(link_widget)
        link_layout.addWidget(link_input)
        link_layout.addWidget(save_button)
        self.link_layout.addWidget(link_widget)

    def save_link(self, link_input):
        link = link_input.text()
        if link:
            self.person.links.append(link)
            self.update_link_layout()

    def edit_link(self, link, link_widget):
        link_layout = link_widget.layout()
        link_label = link_layout.itemAt(0).widget()
        edit_button = link_layout.itemAt(1).widget()
        link_input = QLineEdit(link)
        save_button = QPushButton('Save')
        save_button.clicked.connect(lambda checked, l=link, i=link_input, w=link_widget: self.save_edited_link(l, i, w))
        link_layout.replaceWidget(link_label, link_input)
        link_layout.replaceWidget(edit_button, save_button)
        link_label.setParent(None)
        edit_button.setParent(None)
        link_input.setFocus()

    def save_edited_link(self, old_link, link_input, link_widget):
        new_link = link_input.text()
        if new_link:
            self.person.links.remove(old_link)
            self.person.links.append(new_link)
            self.update_link_layout()

    def delete_link(self, link):
        self.person.links.remove(link)
        self.update_link_layout()

    def add_custom_attribute(self):
        attr_name_input = QLineEdit()
        attr_value_input = QLineEdit()
        save_button = QPushButton('Save')
        save_button.clicked.connect(lambda checked, n=attr_name_input, v=attr_value_input: self.save_custom_attribute(n, v))
        custom_attribute_widget = QWidget()
        custom_attribute_layout = QHBoxLayout(custom_attribute_widget)
        custom_attribute_layout.addWidget(QLabel('Label:'))
        custom_attribute_layout.addWidget(attr_name_input)
        custom_attribute_layout.addWidget(QLabel('Content:'))
        custom_attribute_layout.addWidget(attr_value_input)
        custom_attribute_layout.addWidget(save_button)
        self.custom_attribute_layout.addWidget(custom_attribute_widget)

    def save_custom_attribute(self, attr_name_input, attr_value_input):
        attr_name = attr_name_input.text()
        attr_value = attr_value_input.text()
        if attr_name and attr_value:
            if not hasattr(self.person, 'custom_attributes'):
                self.person.custom_attributes = {}
            self.person.custom_attributes[attr_name] = attr_value
            self.update_custom_attribute_layout()

    def edit_custom_attribute(self, attr_name, attr_value, custom_attribute_widget):
        custom_attribute_layout = custom_attribute_widget.layout()
        custom_attribute_label = custom_attribute_layout.itemAt(0).widget()
        edit_button = custom_attribute_layout.itemAt(1).widget()
        attr_name_input = QLineEdit(attr_name)
        attr_value_input = QLineEdit(attr_value)
        save_button = QPushButton('Save')
        save_button.clicked.connect(lambda checked, n=attr_name, i_n=attr_name_input, i_v=attr_value_input, w=custom_attribute_widget: self.save_edited_custom_attribute(n, i_n, i_v, w))
        delete_button = QPushButton('Delete')
        delete_button.clicked.connect(lambda checked, n=attr_name: self.delete_custom_attribute(n))
        custom_attribute_layout.replaceWidget(custom_attribute_label, attr_name_input)
        custom_attribute_layout.addWidget(QLabel('Content:'))
        custom_attribute_layout.addWidget(attr_value_input)
        custom_attribute_layout.replaceWidget(edit_button, save_button)
        custom_attribute_layout.addWidget(delete_button)
        custom_attribute_label.setParent(None)
        edit_button.setParent(None)
        attr_name_input.setFocus()

    def save_edited_custom_attribute(self, old_attr_name, attr_name_input, attr_value_input, custom_attribute_widget):
        new_attr_name = attr_name_input.text()
        new_attr_value = attr_value_input.text()
        if new_attr_name and new_attr_value:
            del self.person.custom_attributes[old_attr_name]
            self.person.custom_attributes[new_attr_name] = new_attr_value
            self.update_custom_attribute_layout()

    def delete_custom_attribute(self, attr_name):
        del self.person.custom_attributes[attr_name]
        self.update_custom_attribute_layout()

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

    def update_relationship_list(self):
        for i in reversed(range(self.relationship_layout.count())):
            relationship_widget = self.relationship_layout.itemAt(i).widget()
            self.relationship_layout.removeWidget(relationship_widget)
            relationship_widget.deleteLater()

        for relationship in self.person.group.relationships:
            if relationship in self.person.get_relationships():
                people = self.person.get_relationships()[relationship]
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
            self.directed_checkbox.setVisible(True)
        else:
            self.custom_relationship_input.setVisible(False)
            self.directed_checkbox.setVisible(False)

    def update_suggestions(self, text):
        self.suggestion_list.clear()
        if text:
            suggestions = [person for person in self.person.group.people if text.lower() in person.lower()]
            self.suggestion_list.addItems(suggestions)
            self.suggestion_list.setVisible(True)
        else:
            self.suggestion_list.setVisible(False)

    def autofill_relationship(self, item):
        self.relationship_input.setText(item.text())
        self.suggestion_list.setVisible(False)

    def add_relationship(self):
        target_name = self.relationship_input.text()
        relationship_type = self.relationship_type.currentText()

        if relationship_type == 'Custom':
            relationship = self.custom_relationship_input.text()
            if not relationship:
                return
            directed = self.directed_checkbox.isChecked()
        else:
            relationship = relationship_type.lower()
            directed = relationship not in ['friend', 'partner', 'coworker/colleague']

        if target_name:
            if directed:
                self.person.add_directed_relationship(target_name, relationship)
            else:
                self.person.add_undirected_relationship(target_name, relationship)
            self.parent.update_person_list()
            self.relationship_input.clear()
            self.custom_relationship_input.clear()
            self.suggestion_list.setVisible(False)
            self.parent.group.update_relationship_graphs()
            self.update_relationship_list()

    def delete_relationship(self, relationship, person_name):
        self.person.remove_relationship(person_name, relationship)
        self.parent.group.update_relationship_graphs()
        self.update_relationship_list()
    
    def delete_person(self):
        reply = QMessageBox.question(self, 'Delete Person', 'Are you sure you want to delete this person?',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            self.parent.group.remove_person(self.person.fullname)
            self.parent.update_person_list()
            self.parent.person_list.setCurrentRow(-1)
            self.clear_person_details()

    def clear_person_details(self):
        self.person_name_label.clear()
        self.bio_label.setVisible(False)
        self.bio_text.clear()
        self.bio_button.setText('Add Bio')

        while self.attribute_layout.rowCount():
            self.attribute_layout.removeRow(0)

        self.clear_email_layout()
        self.clear_link_layout()
        self.clear_custom_attribute_layout()
        self.clear_relationship_layout()

    def clear_email_layout(self):
        while self.email_layout.count():
            email_widget = self.email_layout.takeAt(0).widget()
            email_widget.deleteLater()

    def clear_link_layout(self):
        while self.link_layout.count():
            link_widget = self.link_layout.takeAt(0).widget()
            link_widget.deleteLater()

    def clear_custom_attribute_layout(self):
        while self.custom_attribute_layout.count():
            custom_attribute_widget = self.custom_attribute_layout.takeAt(0).widget()
            custom_attribute_widget.deleteLater()

    def clear_relationship_layout(self):
        while self.relationship_layout.count():
            relationship_widget = self.relationship_layout.takeAt(0).widget()
            relationship_widget.deleteLater()


def main():
    app = QApplication(sys.argv)

    config = configparser.ConfigParser()
    config.read('config.ini')
    last_saved_file = config.get('DEFAULT', 'last_saved_file')
    last_loaded_file = None

    if last_saved_file:
        group = Group(last_saved_file)
        last_loaded_file = last_saved_file
    else:
        group = Group()

    window = PersonWindow(group)
    window.last_loaded_file = last_loaded_file
    window.show()

    result = app.exec_()

    if result == 0:
        if window.last_loaded_file:
            config.set('DEFAULT', 'last_saved_file', window.last_loaded_file)
            with open('config.ini', 'w') as configfile:
                config.write(configfile)

    sys.exit(result)

if __name__ == '__main__':
    main()