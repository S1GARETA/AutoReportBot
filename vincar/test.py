async def getVin(gosnum):
    now = datetime.datetime.now()
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    payload = "bsoseries=ССС&bsonumber=&requestDate={}" \
              "&vin=&licensePlate={}" \
              "&bodyNumber=&chassisNumber=&isBsoRequest=false&captcha={}".format(now.strftime("%d.%m.%Y"), gosnum,
                                                                                 recaptcha.solution())

    # r = requests.post(url="https://dkbm-web.autoins.ru/dkbm-web-1.0/policyInfo.htm", headers=headers, data=payload.encode('utf-8'), verify=False).json()

    async with aiohttp.ClientSession() as session:
        async with session.post(url="https://dkbm-web.autoins.ru/dkbm-web-1.0/policyInfo.htm", headers=headers,
                                data=payload.encode('utf-8')) as response:
            r = await response.json()

    payload = "processId={}" \
              "&bsoseries=ССС&bsonumber=&vin=&licensePlate={}" \
              "&bodyNumber=&chassisNumber=&requestDate={}" \
              "&g-recaptcha-response=".format(r['processId'], gosnum, now.strftime("%d.%m.%Y"))
    while True:
        # r = requests.post(url="https://dkbm-web.autoins.ru/dkbm-web-1.0/policyInfoData.htm", headers=headers,
        #              data=payload.encode('utf-8'), verify=False)

        async with aiohttp.ClientSession() as session:
            async with session.post(url="https://dkbm-web.autoins.ru/dkbm-web-1.0/policyInfoData.htm", headers=headers,
                                    data=payload.encode('utf-8')) as response:
                r = html.fromstring(await response.read()).xpath('//tr[./td[text()="VIN"]]/td[2]/text()')

        try:
            VIN = r[0]
            break
        except:
            if ('Сведения о договоре ОСАГО с указанными данными не найдены.' in r.text):
                raise ValueError('VIN не найден')
            else:
                continue
    return VIN