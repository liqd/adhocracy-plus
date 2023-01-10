import pytest
from django import forms

from apps.contrib.mixins import ImageRightOfUseMixin
from apps.ideas.models import Idea


class IdeaForm(ImageRightOfUseMixin, forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.module = kwargs.pop("module")
        super().__init__(*args, **kwargs)

    class Meta:
        model = Idea
        fields = ["name", "image"]


@pytest.mark.django_db
def test_add_default(module, idea_factory, ImagePNG):
    idea_no_image = idea_factory()
    form = IdeaForm(module=module, instance=idea_no_image)
    assert "right_of_use" in form.fields
    assert "right_of_use" not in form.initial

    idea_with_image = idea_factory(image=ImagePNG)
    form = IdeaForm(module=module, instance=idea_with_image)
    assert "right_of_use" in form.fields
    assert "right_of_use" in form.initial
    assert form.initial["right_of_use"]


@pytest.mark.django_db
def test_clean(module, idea_factory, ImagePNG):
    idea_with_image = idea_factory(image=ImagePNG)
    data = {
        "right_of_use": False,
    }
    form = IdeaForm(module=module, instance=idea_with_image, data=data)
    assert not form.is_valid()
    assert form["right_of_use"].errors[0].startswith("You want to upload an image.")
