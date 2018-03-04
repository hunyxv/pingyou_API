
CODE_EMAIL_BODY_html = '''
<html xmlns="http://www.w3.org/1999/xhtml">

    <head>
        <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
        <title></title>
    </head>

    <body>
        <table width="650" border="0" cellspacing="0" align="center" cellpadding="0" style="border: #ccc 1px solid;">
            <tbody>
                <tr>
                    <td>

                        <table width="592" border="0" align="center" cellspacing="0" cellpadding="0" style="margin: 28px 28px 10px 28px;">
                            <tbody>
                                <tr>
                                    <td style="font-size: 14px; color: 333333;font-weight: bold;padding-bottom:15px;">
                                        {username}你好：
                                    </td>
                                </tr>
                            </tbody>
                        </table>
                        <table width="592" border="0" align="center" cellspacing="0" cellpadding="0" style="margin: 28px 28px 10px 28px;">
                            <tbody>
                                <tr>
                                    <td style="font-size: 14px; color: 333333; font-weight: bold; padding-bottom:15px;">
                                        验证码：
                                    </td>
                                </tr>
                                <tr>
                                    <td style="font-size: 20px; color: #FC2424; font-weight: bold; padding:30px;" >
                                        {code}
                                    </td>
                                </tr>
                                <tr>
                                    <td>
                                        <br>
                                    </td>
                                </tr>
                                <tr>
                                </tr>
                            </tbody>
                        </table>
                    </td>
                </tr>
            </tbody>
        </table>
    </body>

</html>
'''

CODE_EMAIL_BODY_txt = '''
{username}你好：
验证码：
{code}
'''