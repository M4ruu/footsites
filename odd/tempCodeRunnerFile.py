# Scroll ke bawah halaman secara berulang
    # while True:
    #     content_height = page.evaluate('(document.documentElement || document.body).scrollHeight')
    #     page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
    #     time.sleep(1)
    #     new_content_height = page.evaluate('(document.documentElement || document.body).scrollHeight')
    #     if new_content_height == content_height:
    #         break