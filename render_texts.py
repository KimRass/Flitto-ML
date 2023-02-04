def _apply_word_wrap(text, width):
    new_text = ""
    for subtext in text.split(" "):
        if new_text != "":
            new_text += " "
        new_text += subtext
        if len(new_text.rsplit("\n", 1)[-1]) > width:
            new_text = new_text[: -len(subtext)].strip()
            new_text += "\n"
            new_text += subtext.strip()
    return new_text.strip()


def _get_textbox_width_and_height(ctx, image, text):
    font_metrics = ctx.get_font_metrics(image=image, text=text, multiline=True)
    return (font_metrics.text_width, font_metrics.text_height)


def _get_word_wrapped_text(ctx, image, text, bbox_width, bbox_height, width=0):
    if width == 0:
        width = max(list(map(len, text.split("\n"))))

    textbox_width, textbox_height = _get_textbox_width_and_height(
        ctx=ctx, image=image, text=text
    )
    if textbox_width > bbox_width:
        if width == 1:
            ctx.font_size -= 0.75
        else:
            text = _apply_word_wrap(text=" ".join(text.split("\n")), width=width - 1)
            text = _get_word_wrapped_text(
                ctx=ctx,
                image=image,
                text=text,
                bbox_width=bbox_width,
                bbox_height=bbox_height,
                width=width - 1
            )
    return text