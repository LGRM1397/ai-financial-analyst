import streamlit as st

def init_watchlist():
    if "watchlist" not in st.session_state:
        st.session_state.watchlist = []
    if "watchlist_feedback" not in st.session_state:
        st.session_state.watchlist_feedback = None
    if "watchlist_added_ticker" not in st.session_state:
        st.session_state.watchlist_added_ticker = None

def add_to_watchlist(ticker):
    if ticker and ticker not in st.session_state.watchlist:
        st.session_state.watchlist.append(ticker)
        st.session_state.watchlist_feedback = "added"
        st.session_state.watchlist_added_ticker = ticker
        st.rerun()  # Force UI refresh

def remove_from_watchlist(ticker):
    if ticker in st.session_state.watchlist:
        st.session_state.watchlist.remove(ticker)
        st.session_state.watchlist_removed = ticker
        st.rerun()  # Force UI refresh after removal

def display_watchlist_sidebar():
    st.sidebar.subheader("Your Watchlist")

    if st.session_state.watchlist:
        for saved_ticker in st.session_state.watchlist:
            col1, col2 = st.sidebar.columns([5, 1])
            col1.markdown(f"<span style='font-weight: 500;'>{saved_ticker}</span>", unsafe_allow_html=True)

            if col2.button("X", key=f"remove_{saved_ticker}_btn"):
                remove_from_watchlist(saved_ticker)
                return  # Exit early to prevent rerun conflict
    else:
        st.sidebar.write("Your watchlist is empty.")

    if "watchlist_removed" in st.session_state:
        st.sidebar.success(f"{st.session_state.watchlist_removed} removed.")
        del st.session_state.watchlist_removed

def add_to_watchlist_button(final_ticker):
    if not final_ticker:
        return

    already_added = final_ticker in st.session_state.watchlist

    if not already_added:
        if st.button("Add to Watchlist", key=f"add_btn_{final_ticker}"):
            add_to_watchlist(final_ticker)
    else:
        st.session_state.watchlist_feedback = "exists"
        st.session_state.watchlist_added_ticker = final_ticker

    # Show feedback after rerun
    if (
        st.session_state.watchlist_feedback == "added"
        and st.session_state.watchlist_added_ticker == final_ticker
    ):
        st.success(f"{final_ticker} added to your watchlist.")
    elif (
        st.session_state.watchlist_feedback == "exists"
        and st.session_state.watchlist_added_ticker == final_ticker
    ):
        st.info("This ticker is already in your watchlist.")
