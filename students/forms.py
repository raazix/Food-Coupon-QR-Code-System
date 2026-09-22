from django import forms

class CSVUploadForm(forms.Form):
    csv_file = forms.FileField(
        label='Select students CSV file',
        help_text='Must have columns: Name, USN, Section, Food, Email'
    )
