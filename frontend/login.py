import streamlit as st


def show_login():

    st.title("Welcome Back")

    st.write("Login to continue with DebugGenie")

    st.write("")

    if st.button("← Back to Home"):
        st.session_state.page = "home"
        st.rerun()

    st.write("")

    with st.form("login_form"):

        email = st.text_input("Email")

        password = st.text_input(
            "Password",
            type="password"
        )

        submitted = st.form_submit_button("Login")

        if submitted:

            if not email or not password:

                st.error("Please enter email and password.")

            else:

                from backend.auth import login_user

                user = login_user(
                    email,
                    password
                )

                if user:

                    st.session_state.logged_in = True
                    st.session_state.user_id = user["id"]
                    st.session_state.username = user["name"]
                    st.session_state.user_email = user["email"]
                    st.session_state.user_role = user["role"]

                    st.session_state.page = "dashboard"

                    st.rerun()

                else:

                    st.error("Invalid email or password.")

    st.write("")

    if st.button("Don't have an account? Sign Up"):

        st.session_state.page = "register"

        st.rerun()