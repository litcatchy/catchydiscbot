import discord
from discord.ext import commands
import re
import random

class PFPTrigger(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.triggers = {
            r"\blips?\b": [
                "https://cdn.discordapp.com/attachments/1371136109479858296/1371141905005674617/94d586bb5680e5be1fcc7fbc2e4ac71b.jpg?ex=68220ee8&is=6820bd68&hm=95b70ca1fcd46d5989744bae5fcc0a9ae3227ff229e4145b556ae97e313ca200&",
                "https://cdn.discordapp.com/attachments/1371136109479858296/1371141094531661894/7de72e735d5247283916d54aa34f2765.jpg?ex=68220e27&is=6820bca7&hm=7ae128477b30e842346b7b2cb046bc489b3196654f3e797645baa401918efdcb&",
                "https://cdn.discordapp.com/attachments/1371136109479858296/1371142194014060776/919c21c33540b0ec73678740512ba850.jpg?ex=68220f2d&is=6820bdad&hm=3934d3f6dc7bb066989357fe691c40a9fd57ca9e976939b194aa6fe04c9076d3&",
                "https://cdn.discordapp.com/attachments/1371136109479858296/1371142639306543295/a06bb3bc971964144554967a5ba36dfc.jpg?ex=68220f97&is=6820be17&hm=1fe83bd948f6fe62c7353d54018eb7ffa378e7096bfdc5f20b6005e7e61aae0e&",
                "https://cdn.discordapp.com/attachments/1371136109479858296/1371142900758478938/a4ab707b3f5e7d7e1e9f6f5ac1a3b96a.jpg?ex=68220fd6&is=6820be56&hm=6126aab43185429e7a79bd78bdd9c8cebff60e056772cbb72c439b315079c058&",
                "https://cdn.discordapp.com/attachments/1371136109479858296/1371143315344330772/078143f7d50e0b227bfa6897aca137b8.jpg?ex=68221038&is=6820beb8&hm=1ab1b53e31cbe14319a5340ecf5c9ded943a054e563afc63140cb8aa7fac22fa&",
                "https://cdn.discordapp.com/attachments/1371136109479858296/1371143505585504276/IMG_20250511_204438.jpg?ex=68221066&is=6820bee6&hm=60daf14ac82c03a772ed30a5df170872675abd103d210976a132e2578f20676c&",
                "https://cdn.discordapp.com/attachments/1371136109479858296/1371144002044166296/1dacb85561f831418b4cdf7ecfda1e1e.jpg?ex=682210dc&is=6820bf5c&hm=fa96ddb00430e764d5a813d425cc68e57ba39c93b050f09b2d144f973855ae0e&",
                "https://cdn.discordapp.com/attachments/1371136109479858296/1371144002044166296/1dacb85561f831418b4cdf7ecfda1e1e.jpg?ex=682210dc&is=6820bf5c&hm=fa96ddb00430e764d5a813d425cc68e57ba39c93b050f09b2d144f973855ae0e&",
                "https://cdn.discordapp.com/attachments/1371136109479858296/1371144238745780267/6b15673c6fb03f5aed0c8ce88feaea05.jpg?ex=68221115&is=6820bf95&hm=919f4258a09606888de912d63d6d4f3cda1a054eecb71d73bd7b27fdd8fe3728&",
                "https://cdn.discordapp.com/attachments/1371136109479858296/1371144253366861874/03c8ae2982747a0a755d549090f37530.jpg?ex=68221118&is=6820bf98&hm=61eb726a496ec8c131a3cb021e9f22c599038404ae3752eaaab1570eef2e7de9&",
                "https://cdn.discordapp.com/attachments/1371136109479858296/1371144264465256558/6a6ba9e582ec4e07e9904da3899fe061.jpg?ex=6822111b&is=6820bf9b&hm=6f79a4d4306d0caabe06b6be67dc99753d0e759eb40c67d3204b99023ea922bd&",         
            ],
            r"\beyes?\b": [
                "https://cdn.discordapp.com/attachments/1371136109479858296/1371150574673727488/27a2a2b08420e52583248522b7db7335.jpg?ex=682216fb&is=6820c57b&hm=1cf3557a6233ac1f2c2b35a5c5e2f371b0da1553bffe429b5150900b21222a4c&",
                "https://cdn.discordapp.com/attachments/1371136109479858296/1371150597893525598/fa23478f3b1a218f05d57929fe78bfe9.jpg?ex=68221701&is=6820c581&hm=9689d09e40aa8c807f56773304a379c432e1d57c1472f145d333bc35dd1c0ed5&",
                "https://cdn.discordapp.com/attachments/1371136109479858296/1371150585520459868/0b13054f492585f306f6dfdf169f7985.jpg?ex=682216fe&is=6820c57e&hm=f2a9404513b52c8612ff9a6d72d61c34f079e68cf57eb1f32080ce82f79c9451&",
            ],
            r"\bboobs?\b": [
                "https://cdn.discordapp.com/attachments/1371136109479858296/1371136182003568791/9f6689276a87c4b62783606df6d75445.jpg?ex=68220994&is=6820b814&hm=049116be1164956b958e3bf7b393bb7d524a5a0ffa9ccc5d7dc422d64d040c72&",
                "https://cdn.discordapp.com/attachments/1371136109479858296/1371137298795724800/9bd728af589af668f150ab9f037b90cf.jpg?ex=68220a9e&is=6820b91e&hm=78ceb30b90305381ef248ae3378c54df5273ae3e9d24a9365a3a638c7d172e35&",
                "https://cdn.discordapp.com/attachments/1371136109479858296/1371139160144089178/fcc9f273fcc62b217efb69cad994c9d5.jpg?ex=68220c5a&is=6820bada&hm=1ec36f42e85325f74eb90a959d32d68b8e9615493ec684c580989c393ae9e695&",
                "https://cdn.discordapp.com/attachments/1371136109479858296/1371141094531661894/7de72e735d5247283916d54aa34f2765.jpg?ex=68220e27&is=6820bca7&hm=7ae128477b30e842346b7b2cb046bc489b3196654f3e797645baa401918efdcb&",
                "https://cdn.discordapp.com/attachments/1371136109479858296/1371146362149802054/IMG_20250511_205454.jpg?ex=6822130f&is=6820c18f&hm=f4a6a96f9cb39879af7b194dd7dbb8338f0510d3a7baaaf83bb007020c187402&",
                "https://cdn.discordapp.com/attachments/1371136109479858296/1371146351588675654/b58c96ec0785ef7a3c511dfa9d51864a.jpg?ex=6822130c&is=6820c18c&hm=73519d91fdff71bf200973edb7e7be0ad0b7b27573ee0651de541c5541a409e9&",
                "https://cdn.discordapp.com/attachments/1371136109479858296/1371146374896422982/c2789544d03bb27dbb232c03b943fb66.jpg?ex=68221312&is=6820c192&hm=112d68bd9c177ff45e0e3094510a8597831f688d7b8b9073c65f419618cff98d&",
                "https://cdn.discordapp.com/attachments/1371136109479858296/1371146387470811326/633cc3a55c343fa83840fe79c48845cf.jpg?ex=68221315&is=6820c195&hm=d591c5fefa9565a9723e4c69577b10a876545cc75520d6f7f40d83bc4cf113c0&",
                "https://cdn.discordapp.com/attachments/1371136109479858296/1371146422891843715/589eddc62b728289eaf4dead084276bb.jpg?ex=6822131d&is=6820c19d&hm=e85f81fc60c8c1a264d77cffbd2e4647c3666103006bac8a91f996d5c309ed20&",
                "https://cdn.discordapp.com/attachments/1371136109479858296/1371146400947114094/26c0ddd3ad777b805dc7cd1037da8944.jpg?ex=68221318&is=6820c198&hm=0c1a0520dc8ead1dcdd31dffa8bafa713169f87610e730215dd1a075f803346b&",
                "https://cdn.discordapp.com/attachments/1371136109479858296/1371146533042389123/7040ef8647c1909161989ed91aadfc75.jpg?ex=68221338&is=6820c1b8&hm=ce5dacbc9cf1da7cfb9716fc3611a6f4b834eff194166c8e4fad88d3141cfcf6&",
                "https://cdn.discordapp.com/attachments/1371136109479858296/1371146544153235567/c07d1030aa0c62cd5df2219b32b2fe7f.jpg?ex=6822133a&is=6820c1ba&hm=661bed317a664598b6c957739254ae0d00600dac818f4209dbe12b8ce47c66df&",
                "https://cdn.discordapp.com/attachments/1371136109479858296/1371147762787291348/8a80773a42a3dcbd5c30ec63d03afd43.jpg?ex=6822145d&is=6820c2dd&hm=5aa7ba23b98b97b3078ea161209f6864ac6e596cb1e95d16776d9967e04188e5&",
                "https://cdn.discordapp.com/attachments/1371136109479858296/1371148471855480882/7858af8c679f5c57ca8798508c26a315.jpg?ex=68221506&is=6820c386&hm=71fae4d9d458a0460fbe7bbed76bd77ed0a847796935d504ee1d4a9b8b0cca4a&",
                "https://cdn.discordapp.com/attachments/1371136109479858296/1371147762787291348/8a80773a42a3dcbd5c30ec63d03afd43.jpg?ex=6822145d&is=6820c2dd&hm=5aa7ba23b98b97b3078ea161209f6864ac6e596cb1e95d16776d9967e04188e5&",
                "https://cdn.discordapp.com/attachments/1371136109479858296/1371148461612732497/996b30fd6b46182bf7e20860d50a83c1.jpg?ex=68221503&is=6820c383&hm=a9ee949f6050b823b21d869087cf9053296a91438ccf2082bb9819798d2b126b&",
                "https://cdn.discordapp.com/attachments/1371136109479858296/1371148747270262957/0f4a06fed15562c4ab36b26f085e5622.jpg?ex=68221548&is=6820c3c8&hm=e647328abf70269a37a6026ac9396f292a80809edc8c363ec9532bb65fa4dd31&",
                "https://cdn.discordapp.com/attachments/1371136109479858296/1371148761002414160/86d8a799f3319f35ff7f29811fceffea.jpg?ex=6822154b&is=6820c3cb&hm=b1e600562509fb9adb645ee92dd09c977f01ad383e46c11510474ac33dd16f2d&",
                "https://cdn.discordapp.com/attachments/1371136109479858296/1371148773329207306/94ae21d27f352062cc1fcaed5ea5535d.jpg?ex=6822154e&is=6820c3ce&hm=8cd8502ff95f3fa2b1d80ce4d93ee1895d5e29ebaa50899d327c3cda2737973a&",
                "https://cdn.discordapp.com/attachments/1371136109479858296/1371149092587311205/3903016895af38e87645efd9e72c762c.jpg?ex=6822159a&is=6820c41a&hm=94a55e585ffcb7aaec5daf4223fae56f65d6ce2fe11a73a250d09db3867072e1&",
                "https://cdn.discordapp.com/attachments/1371136109479858296/1371149104725360672/7ad79dd6afeb6a31312bc46dd64e3b54.jpg?ex=6822159d&is=6820c41d&hm=f4c4918eff6a63a71f721e54a9b5ed6c452daf5eb370ca5af00350be35182c2f&",
            ],
            r"\bwaists?\b": [
                "https://cdn.discordapp.com/attachments/1371136109479858296/1371149451959341279/9c4b2ef43ce97cc19d894cedb896bd60.jpg?ex=682215f0&is=6820c470&hm=a5e3b81248a491ff760455566bdba1fb953e8a3922ac4ce65bc108e1e37f3beb&",
                "https://cdn.discordapp.com/attachments/1371136109479858296/1371149438533505104/711850b7c4877e474f837b3d387e6040.jpg?ex=682215ec&is=6820c46c&hm=5bf7aa847d5f3035e26aa1f472808e795f573a6c6dedfba69d75449933af7ad9&",
                "https://cdn.discordapp.com/attachments/1371136109479858296/1371149463082500128/cb72d6dc0a32cbea4cb11c9d8677b7e7.jpg?ex=682215f2&is=6820c472&hm=f8ccae534645d07a15ee7693ade0e8c0e3761acff94671d0246ebf8574a57c06&",
            ],
            r"\babs?\b": [
                "https://cdn.discordapp.com/attachments/1371136109479858296/1371151083329814669/40fb9b3fbcd7a69a6c6874727208daf1.jpg?ex=68221775&is=6820c5f5&hm=bef97eeb192301b84c70d2eee3a93188d10c8d7fbe08c115c851c6b03263c75e&",
                "https://cdn.discordapp.com/attachments/1371136109479858296/1371151071355076659/8d558c774ef8d8eeefaacd5217dbc85a.jpg?ex=68221772&is=6820c5f2&hm=82147f7c17617b746adbe444f276bf32e8f50b78c4b904d4a1f1d8c310c7708d&",
                "https://cdn.discordapp.com/attachments/1371136109479858296/1371151060374130768/d073a0aaa07467ee28894c940efbe1c3.jpg?ex=6822176f&is=6820c5ef&hm=a06a1a1e533f050ba4d23c137e60bddf5a069a6bf43c748076833726848d1831&",
            ],
            r"\bass(es)?\b": [
                "https://cdn.discordapp.com/attachments/1371136109479858296/1371150070103277668/0a3477160b18a50f35d8523c0ad087ef.jpg?ex=68221683&is=6820c503&hm=b096321ea7f3df321657aae26b1fd1bdaff9ed41d9fbb076c6aa78fa82b0bb91&",
                "https://cdn.discordapp.com/attachments/1371136109479858296/1371150059147759616/2562d0bf6668abe7b83b4b7bf1f4a1b5.jpg?ex=68221680&is=6820c500&hm=9c1170c6365773d2899631da632f7346a84d22849060d397b8939beba204c33a&",
                "https://cdn.discordapp.com/attachments/1371136109479858296/1371150044975206472/63b93443e40ffe86d20c000c951df752.jpg?ex=6822167d&is=6820c4fd&hm=fdb0ca980b20fd8b51e87e5de299ab76392e5b285475adb41cfd12fa2791fc91&",
            ],
            r"\bbiceps?\b": [
                "https://cdn.discordapp.com/attachments/1371136109479858296/1371151431314440476/c1993606e68f0b290626ff7034b933ab.jpg?ex=682217c7&is=6820c647&hm=2c2caafbd640add6c45f8ecbb3a0d1098d237e57a35c110a15fbce1f465ae23b&",
                "https://cdn.discordapp.com/attachments/1371136109479858296/1371151443616206992/dc8ad8446c62daff1c0056773cf5f5f9.jpg?ex=682217ca&is=6820c64a&hm=f9582bdc37abe33078a31cfd4f7ff8d27e330d13c9dbccc559d572f9ba992194&",
                "https://cdn.discordapp.com/attachments/1371136109479858296/1371151443616206992/dc8ad8446c62daff1c0056773cf5f5f9.jpg?ex=682217ca&is=6820c64a&hm=f9582bdc37abe33078a31cfd4f7ff8d27e330d13c9dbccc559d572f9ba992194&",
            ],
            r"\bveins?\b": [
                "https://cdn.discordapp.com/attachments/1371136109479858296/1371151808793415822/61fa8a704dd2a30b9071c2990ba8719a.jpg?ex=68221821&is=6820c6a1&hm=0b976d36b17e1541013b17c575fefd9494e34ae5b15768f84b64fcf16409bb30&",
                "https://cdn.discordapp.com/attachments/1371136109479858296/1371151825021042800/72cf336a516de3b283675347fde59951.jpg?ex=68221825&is=6820c6a5&hm=c30c4364bc66ac1725e36a4b5a2531e99c164e10e171027bfc2188269ffcfc59&",
                "https://cdn.discordapp.com/attachments/1371136109479858296/1371151835225784380/bef5249fb8e7a3014f20d912a39d3ce7.jpg?ex=68221828&is=6820c6a8&hm=360e702d190d78c255832b70420d06e231447e1387d21a30c603bf481798c5d3&",
            ],
            r"\bhunter eyes?\b": [
                "https://cdn.discordapp.com/attachments/1371136109479858296/1371154310959862001/2c7d2f3c3615e768263bdf6914e4f462.jpg?ex=68221a76&is=6820c8f6&hm=01fbd6dd8b2274999ec1127462267a453b2f0a21141eabfbd1f550566ff7c393&",
                "https://cdn.discordapp.com/attachments/1371136109479858296/1371154322624348246/836640f95b27bd0c1dfe0cb4cce6b24d.jpg?ex=68221a79&is=6820c8f9&hm=3213e9279d909a874e903bfe0343942296f1819d887da5d8a65ebbbf42497c72&",
                "https://cdn.discordapp.com/attachments/1371136109479858296/1371154335483957338/872ce53d9649e230c0e3f1761b3afd1b.jpg?ex=68221a7c&is=6820c8fc&hm=c6274f2cebf2915852da8fc42346da41cf1e565e5218ca30a1292167b97d500b&",
            ],
            r"\bhands?\b": [
                "https://cdn.discordapp.com/attachments/1371136109479858296/1371154072937168956/dd8e86b01e8ce47b9c3ac498ab6b8d95.jpg?ex=68221a3d&is=6820c8bd&hm=c378640435f1685fe1f83d58ab5f5137bbd55b74236f0e8a3843b7d85eae5f5c&",
                "https://cdn.discordapp.com/attachments/1371136109479858296/1371154083599093890/8e9d7789867a158a9099c38655917cd2.jpg?ex=68221a40&is=6820c8c0&hm=5e0a45d281a22143f30ac4fa59ce48ca4735ec496881729bc3e052d04e89ae90&",
                "https://cdn.discordapp.com/attachments/1371136109479858296/1371154095792197682/97e9cf6205834f51cf9a8c5d5954d4ac.jpg?ex=68221a43&is=6820c8c3&hm=4d4aa1b7f28cd65d74fdcaabbed15aa3dacb718386e4cd79a99fa655388d2786&",
            ],
            r"\bchoke\b": [
                "https://cdn.discordapp.com/attachments/1371136109479858296/1371152127208067162/401942f875679fbfb0701da2569d4204.jpg?ex=6822186d&is=6820c6ed&hm=f23ce43f2fe864e929bce2234218fe54da52d3bcfcded7c8e771b91c411a67ed&",
                "https://cdn.discordapp.com/attachments/1371136109479858296/1371152137530376325/07f0b8fb791fa5b7ddefdabbd0adc0aa.jpg?ex=68221870&is=6820c6f0&hm=aa712e8c72ef4d015e2c900ab08bf356ce7549697f0633de7fbb3bf1cf323928&",
                "https://cdn.discordapp.com/attachments/1371136109479858296/1371152106500657172/e29b070c963eb2d76340f36539664a3c.jpg?ex=68221868&is=6820c6e8&hm=1073674fa04b08963dcd9535909a6124b2446c01731ac16d337a4c1f505b446a&",
            ],
            r"\bbaths?\b|\bbathe?\b": [
                "https://cdn.discordapp.com/attachments/1371136109479858296/1371154702015922288/4cdc62e63d5e42d8c72ab00a15ea646d.jpg?ex=68221ad3&is=6820c953&hm=dd0050a06cf13bd5e7e7b69e085ec79a6b6aef514f161f1b0fc0eb52903f91b4&",
                "https://cdn.discordapp.com/attachments/1371136109479858296/1371154726015471676/2aba26c6889aff8f7152d07430dcf7c8.jpg?ex=68221ad9&is=6820c959&hm=ea323e8df8bd6a4457e831530d44a5ccd57a9dddea2df4958a20167793aa73c5&",
                "https://cdn.discordapp.com/attachments/1371136109479858296/1371154713537544282/abb504be07352a4a1c831287261e9f16.jpg?ex=68221ad6&is=6820c956&hm=991c2c2fcc0026b819bb07e0d18ce24ff5f876c1388d2ce7030a59bece757b54&",
            ],
            r"\bfeet\b": [
                "https://cdn.discordapp.com/attachments/1371136109479858296/1371155234771964024/af4c2478fd8b2fb66a93590165b30c9d.jpg?ex=68221b52&is=6820c9d2&hm=27a76d61d83a9b93848662dd2cf45537e887eb7f5da48c8c8734c1bd3953577b&",
                "https://cdn.discordapp.com/attachments/1371136109479858296/1371152641127747784/5c73df73ef5041d975fe2a3589efab6b.jpg?ex=682218e8&is=6820c768&hm=a28edfe13d9a6de3f9dc968f5625228bd4073297b1a93d9b46d8e00d0bd6807f&",
                "https://cdn.discordapp.com/attachments/1371136109479858296/1371152641127747784/5c73df73ef5041d975fe2a3589efab6b.jpg?ex=682218e8&is=6820c768&hm=a28edfe13d9a6de3f9dc968f5625228bd4073297b1a93d9b46d8e00d0bd6807f&",
            ],
            r"\bback\b": [
                "https://cdn.discordapp.com/attachments/1371136109479858296/1371155234771964024/af4c2478fd8b2fb66a93590165b30c9d.jpg?ex=68221b52&is=6820c9d2&hm=27a76d61d83a9b93848662dd2cf45537e887eb7f5da48c8c8734c1bd3953577b&&is=6820c761&hm=1419be5750a176e621caa648e66399e32e45ecab4bd3b6aae8c8f6ae6e39aba9&",
                "https://cdn.discordapp.com/attachments/1371136109479858296/1371155247329968159/536f2a8d1d52d21625ce9042588f5065.jpg?ex=68221b55&is=6820c9d5&hm=05b9f651636dfcccc5ee81aedf60d747b9307ee5ea47c7937612342e5638d288&",
                "https://cdn.discordapp.com/attachments/1371136109479858296/1371155257379520603/151187e3030379476bfd0626d5a0fc95.jpg?ex=68221b58&is=6820c9d8&hm=e07ba9444c18b44c76aa8f1319c26c1c5396bd20e322ba805276b2ed5333a336&",
                        ]
        }

        self.sent_images = {pattern: [] for pattern in self.triggers}

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        for pattern, urls in self.triggers.items():
            if re.search(pattern, message.content, re.IGNORECASE):
                available = [u for u in urls if u not in self.sent_images[pattern]]

                if not available:
                    self.sent_images[pattern] = []
                    available = urls

                selected = random.choice(available)
                self.sent_images[pattern].append(selected)

                await message.channel.send(selected, delete_after=6)
                break

async def setup(bot):
    await bot.add_cog(PFPTrigger(bot))
