INSERT INTO `User_settings` (highlight_words,
            whois_username,
            whois_realname,
            global_nickname,
            hide_joinpartquit_messages,
            show_seconds,
            show_video_previews,
            show_image_previews,
            Registred_users_userID)
			values (%s, %s, %s, %s, %s, %s, %s, %s, %s)
ON DUPLICATE KEY UPDATE highlight_words=%s,
						whois_username=%s,
						whois_realname=%s,
                        global_nickname=%s,
                        hide_joinpartquit_messages=%s,
                        show_seconds=%s,
                        show_video_previews=%s,
                        show_image_previews=%s);
