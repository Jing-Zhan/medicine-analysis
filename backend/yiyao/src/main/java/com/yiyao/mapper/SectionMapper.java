package com.yiyao.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.yiyao.entity.SectionEntity;
import org.apache.ibatis.annotations.Select;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface SectionMapper extends BaseMapper<SectionEntity> {
}
