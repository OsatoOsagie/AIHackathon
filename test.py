#Change the chatbot icon
@cl.set_chat_profiles
async def chat_profile():
    return [
    cl.ChatProfile(
            name="Zenith Care",
            #markdown_description="The underlying model is **GPT-3.5**.",
            icon="/public/favicon.png",
        )
    ]