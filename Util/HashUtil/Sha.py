# encoding:utf-8
__author__ = '130803'
import hashlib


def sha1(str):
    if isinstance(str, unicode):
        str.encode('utf-8')
    hash = hashlib.sha1()
    hash.update(str)
    return hash.hexdigest()

if __name__ == '__main__':
    s = '23樓空拋15公斤啞鈴　台大畢業名醫幹的台北車站附近日前發生，有人將整組近15公斤重的啞鈴外拋，槓片等零件四散，還砸凹一部轎車車頂，幸無人受傷。而警方逮到人發現，嫌犯竟然是一名醫師！   《蘋果》報導，警方調查，住在台北車站前亞洲廣場大樓23樓的陳姓神經內科男醫師（43歲），單身未婚，經常至大樓6樓的健身房運動，因為合約糾紛雙方屢屢發生爭執。日前陳醫師到健身房時，健身房幹部再度「提醒」須延展合約，令陳不滿，隔天凌晨時竟將家裡一組啞鈴從23樓扔出窗外，10分鐘後他下樓察看，發現並未造成傷亡，隨後他又持美工刀下樓割毀健身房位在一樓的廣告帆布洩憤。陳醫師昨晚也向《蘋果》投訴，自稱是新北一家醫院神經內科醫師，強調是因為消費糾紛不甘健身房不理會，才憤而從住家丟下啞鈴。警方昨訊後已依恐嚇危安罪嫌將陳醫師移送法辦。   《中國時報》報導，據了解，陳姓名醫是台大醫學系畢業，擁有高學歷，竟然會因糾紛，情緒失控任意丟擲重物，幸好是沒砸中人，否則救人的醫師，恐成為殺人的凶手，讓承辦員警相當驚訝。（即時新聞中心／綜合報導）   【蘋論陣線】：最新評論及獨立媒體每日總覽'

    # s = s.decode('utf-8')
    print sha1(s)
