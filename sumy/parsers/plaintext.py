# -*- coding: utf8 -*-

from __future__ import absolute_import
from __future__ import division, print_function, unicode_literals

from .._compat import to_unicode
from ..utils import cached_property
from ..models.dom import Sentence, Paragraph, ObjectDocumentModel
from .parser import DocumentParser


class PlaintextParser(DocumentParser):
    @classmethod
    def from_string(cls, string, tokenizer):
        return cls(string, tokenizer)

    @classmethod
    def from_file(cls, file_path, tokenizer):
        with open(file_path) as file:
            return cls(file.read(), tokenizer)

    def __init__(self, text, tokenizer):
        super(PlaintextParser, self).__init__(tokenizer)
        self._text = to_unicode(text).strip()

    @cached_property
    def significant_words(self):
        words = []
        for paragraph in self.document.paragraphs:
            for sentence in paragraph:
                if sentence.is_heading:
                    words.extend(sentence.words)

        if words:
            return tuple(words)
        else:
            return self.SIGNIFICANT_WORDS

    @cached_property
    def stigma_words(self):
        return self.STIGMA_WORDS

    @cached_property
    def document(self):
        current_paragraph = []
        paragraphs = []
        for line in self._text.splitlines():
            line = line.strip()
            if line.isupper():
                heading = Sentence(line, self._tokenizer, is_heading=True)
                current_paragraph.append(heading)
            elif not line and current_paragraph:
                sentences = self._to_sentences(current_paragraph)
                paragraphs.append(Paragraph(sentences))
                current_paragraph = []
            elif line:
                current_paragraph.append(line)

        sentences = self._to_sentences(current_paragraph)
        paragraphs.append(Paragraph(sentences))

        return ObjectDocumentModel(paragraphs)

    def _to_sentences(self, lines):
        text = ""
        sentence_objects = []

        for line in lines:
            if isinstance(line, Sentence):
                if text:
                    sentences = self.tokenize_sentences(text)
                    sentence_objects += map(self._to_sentence, sentences)

                sentence_objects.append(line)
                text = ""
            else:
                text += " " + line

        text = text.strip()
        if text:
            sentences = self.tokenize_sentences(text)
            sentence_objects += map(self._to_sentence, sentences)

        return sentence_objects

    def _to_sentence(self, text):
        assert text.strip()
        return Sentence(text, self._tokenizer)
