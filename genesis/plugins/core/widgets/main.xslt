<xsl:template match="topcategory">
    <a class="ui-el-top-category{x:iif(@selected, ' selected', '')}" href="#" onclick="return Genesis.selectCategory('{@id}');" id="{@id}">
        <i class="{@iconfont}"></i>
        &#160;<xsl:value-of select="@text"/>
            <xsl:if test="@counter != 'None'">
                &#160;<span class="badge"><xsl:value-of select="@counter"/></span>
            </xsl:if>
    </a>
</xsl:template>

<xsl:template match="category">
    <a href="#" onclick="return Genesis.selectCategory('{@id}');">
	    <div id="{@id}" class="ui-el-category {x:iif(@selected, 'selected', '')}">
            <i class="{@iconfont}"></i>&#160;
            <span class="text">
                <xsl:value-of select="@name"/>
            </span>
            <xsl:if test="@counter != 'None'">
                &#160;<span class="badge"><xsl:value-of select="@counter"/></span>
            </xsl:if>
        </div>
    </a>
</xsl:template>

<xsl:template match="categoryfolder">
    <div class="ui-el-categoryfolder" id="{@id}">
        <xsl:value-of select="@text"/>
    </div>
    <div class="ui-el-categoryfolder-children">
        <xsl:apply-templates />
    </div>
</xsl:template>


<xsl:template match="systemmessage">
    <div class="alert alert-{@cls}">
        <xsl:value-of select="@text" />
    </div>
</xsl:template>
