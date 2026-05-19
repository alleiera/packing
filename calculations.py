def calculate_weights(gross_weight, boxes, empty_box_weight, empty_pallet_weight):
    """
    ağarlık kısımları için biz bürüt ağarlık yazacağız aplikasyon koli ağarlığını ve net ağarlığı kendisi otomatik hesaplayacak.
    ayarlar kısmına boş koli ve palet ağarlığını yazabilmek için de bir bölüm eklemeliyiz.
    bu sayede satırdaki koli adeti ile boş koli adeti çarpılır üzerine boş palet ağırlığıda eklenir
    ve bürüt ağırlıktan çıkarttığımızda net ağırlık bulunabilir.
    ayrıca bürüt ağırlıktan boş palet ağırlığını çıkartıp, koli adetine böldüğümüzde de koli ağırlığını bulmuş oluruz.
    """
    try:
        gross = float(gross_weight)
        box_count = int(boxes)
        e_box = float(empty_box_weight)
        e_pallet = float(empty_pallet_weight)
    except (ValueError, TypeError):
        return 0, 0

    if box_count <= 0:
        return 0, 0

    # koli ağırlığı = (bürüt ağırlık - boş palet ağırlığı) / koli adeti
    # Note: The user said "bürüt ağırlıktan boş palet ağırlığını çıkartıp, koli adetine böldüğümüzde de koli ağırlığını bulmuş oluruz."
    # This seems to be the weight of ONE box (including product and empty box) but excluding pallet.
    box_weight = (gross - e_pallet) / box_count

    # net ağırlık = bürüt ağırlık - (koli adeti * boş koli ağırlığı) - boş palet ağırlığı
    # The user said: "satırdaki koli adeti ile boş koli adeti çarpılır üzerine boş palet ağırlığıda eklenir ve bürüt ağırlıktan çıkarttığımızda net ağırlık bulunabilir."
    net_weight = gross - (box_count * e_box) - e_pallet

    return round(box_weight, 2), round(net_weight, 2)
