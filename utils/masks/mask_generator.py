"""
Binary Mask Generation
"""

from utils.logger import logger

def mask_generation(args, root_path: str, chart_id: str, mask_id: str, threshold: int=10):
    if args.chart_type == '[TODO] 1_bar':
        logger.info(f"[Mask Generation] Bar Chart | Chart ID: {chart_id}")
        from constructor.masks.bar_mask import bar_mask_generation
        bar_mask_generation(args, root_path, chart_id, mask_id, threshold)

    # elif args.chart_type == '[TODO] 2_histogram':
    #     logger.info(f"[Mask Generation] Histogram Chart | Chart ID: {chart_id}")
    #     from constructor.masks.histogram_mask import histogram_mask_generation
    #     histogram_mask_generation(args, root_path, chart_id, mask_id, threshold)

    # elif args.chart_type == '[TODO] 12_radar':
    #     logger.info(f"[Mask Generation] Radar Chart | Chart ID: {chart_id}")
    #     from constructor.masks.radar_mask import radar_mask_generation
    #     radar_mask_generation(args, root_path, chart_id, mask_id, threshold)
    
    # else:
    #     logger.info(f"[Mask Generation] Chart ID: {chart_id}")
    #     from constructor.masks.gmask import general_mask_generation
    #     general_mask_generation(args, root_path, chart_id, mask_id, threshold)