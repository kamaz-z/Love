from django import forms

from .models import Moment


class MultipleImageInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleImageField(forms.ImageField):
    widget = MultipleImageInput

    def clean(self, data, initial=None):
        if not data:
            return []
        if not isinstance(data, (list, tuple)):
            data = [data]
        return [super().clean(image, initial) for image in data]


class MomentForm(forms.ModelForm):
    additional_images = MultipleImageField(
        required=False,
        label='Додаткові фото (необов’язково)',
        widget=MultipleImageInput(
            attrs={
                'class': 'w-full rounded-xl border border-gray-200 bg-white px-4 py-2.5 text-sm',
                'accept': 'image/*',
            }
        ),
    )

    class Meta:
        model = Moment
        fields = (
            'title',
            'description',
            'date',
            'period',
            'category',
            'location',
            'image',
        )
        labels = {
            'title': 'Назва спогаду',
            'description': 'Опис',
            'date': 'Дата',
            'period': 'Період',
            'category': 'Категорія',
            'location': 'Місце',
            'image': 'Фото',
        }
        error_messages = {
            'title': {'required': 'Це поле обов’язкове.'},
            'description': {'required': 'Це поле обов’язкове.'},
            'date': {'required': 'Це поле обов’язкове.'},
        }
        widgets = {
            'title': forms.TextInput(
                attrs={
                    'class': 'w-full rounded-xl border border-gray-200 px-4 py-2.5 text-sm focus:border-rose-400 focus:outline-none',
                    'placeholder': 'Наприклад: Наше перше побачення',
                }
            ),
            'description': forms.Textarea(
                attrs={
                    'class': 'w-full rounded-xl border border-gray-200 px-4 py-2.5 text-sm focus:border-rose-400 focus:outline-none',
                    'rows': 4,
                    'placeholder': 'Опишіть цей особливий момент...',
                }
            ),
            'date': forms.DateInput(
                attrs={
                    'class': 'w-full rounded-xl border border-gray-200 px-4 py-2.5 text-sm focus:border-rose-400 focus:outline-none',
                    'type': 'date',
                }
            ),
            'period': forms.Select(
                attrs={
                    'class': 'w-full rounded-xl border border-gray-200 bg-white px-4 py-2.5 text-sm focus:border-rose-400 focus:outline-none',
                }
            ),
            'category': forms.Select(
                attrs={
                    'class': 'w-full rounded-xl border border-gray-200 bg-white px-4 py-2.5 text-sm focus:border-rose-400 focus:outline-none',
                }
            ),
            'location': forms.TextInput(
                attrs={
                    'class': 'w-full rounded-xl border border-gray-200 px-4 py-2.5 text-sm focus:border-rose-400 focus:outline-none',
                    'placeholder': 'Де це сталося? (необов’язково)',
                }
            ),
            'image': forms.ClearableFileInput(
                attrs={
                    'class': 'w-full rounded-xl border border-gray-200 bg-white px-4 py-2.5 text-sm',
                    'accept': 'image/*',
                }
            ),
        }
