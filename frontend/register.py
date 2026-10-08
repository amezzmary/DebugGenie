import streamlit as st


def show_register():

    st.title("Create Your Account")

    st.write(
        "Join DebugGenie and start debugging smarter."
    )

    st.write("")

    # Back to Home
    if st.button("← Back to Home"):
        st.session_state.page = "home"
        st.rerun()

    st.write("")

    # Registration form
    with st.form("register_form"):

        name = st.text_input(
            "Full Name",
            placeholder="Enter your name"
        )

        email = st.text_input(
            "Email",
            placeholder="Enter your email"
        )

        password = st.text_input(
            "Password",
            type="password",
            placeholder="Create a password"
        )

        confirm_password = st.text_input(
            "Confirm Password",
            type="password",
            placeholder="Confirm your password"
        )

        submitted = st.form_submit_button(
            "Create Account",
            use_container_width=True
        )

        if submitted:

            if not name or not email or not password:

                st.error(
                    "Please fill in all fields."
                )

            elif password != confirm_password:

                st.error(
                    "Passwords do not match."
                )

            else:

                try:

                    from backend.auth import register_user

                    result = register_user(
                        name,
                        email,
                        password
                    )

                    if result:

                        st.success(
                            "Account created successfully!"
                        )

                        st.info(
                            "You can now login."
                        )

                    else:

                        st.error(
                            "This email is already registered."
                        )

                except Exception as e:

                    st.error(
                        f"Registration error: {e}"
                    )

    st.write("")

    # Login
    if st.button(
        "Already have an account? Login",
        use_container_width=True
    ):

        st.session_state.page = "login"
        st.rerun()