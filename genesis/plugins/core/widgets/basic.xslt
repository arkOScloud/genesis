<xsl:template match="label">
    <xsl:choose>
        <xsl:when test="@size = '5'">
            <h1 class="page-header"><xsl:value-of select="@text" /></h1>
        </xsl:when>
        <xsl:when test="@size = '4'">
            <h2 class="page-header"><xsl:value-of select="@text" /></h2>
        </xsl:when>
        <xsl:when test="@size = '3'">
            <h3 class="page-header"><xsl:value-of select="@text" /></h3>
        </xsl:when>
        <xsl:when test="@size = 'lead'">
            <p class="lead"><xsl:value-of select="@text" /></p>
        </xsl:when>
        <xsl:otherwise>
            <span class="ui-el-label-{x:attr(@size, '1')} {x:iif(@fade, 'text-muted', '')} {@class}" style="{x:iif(@bold, 'font-weight: bold;', '')} {x:iif(@monospace, 'font-family: monospace;', '')} {x:iif(@lbreak, 'max-width: 500px;', '')}">
                <xsl:value-of select="@text" />
            </span>
        </xsl:otherwise>
    </xsl:choose>
</xsl:template>


<xsl:template match="image">
    <xsl:choose>
        <xsl:when test="@lightbox != ''">
            <a href="{@file}" data-lightbox="{@lightbox}">
                <img id='{@id}' class="{x:attr(@cls, 'ui-el-image')}" src="{@file}" style="width: {x:css(@width, 'auto')}; height: {x:css(@height, 'auto')};" />
            </a>
        </xsl:when>
        <xsl:otherwise>
            <img id='{@id}' class="{x:attr(@cls, 'ui-el-image')}" src="{@file}" style="width: {x:css(@width, 'auto')}; height: {x:css(@height, 'auto')};" />
        </xsl:otherwise>
    </xsl:choose>
</xsl:template>


<xsl:template match="toolbar">
    <xsl:apply-templates />
    <hr />
</xsl:template>

<!-- Button magic -->
<xsl:template match="buttongroup">
    <div id="{@id}" class="btn-group{x:iif(@size = 'lg', ' btn-group-lg', '')}">
        <xsl:apply-templates />
    </div>
</xsl:template>

<xsl:template match="inputgroup">
    <div class="input-group {@class}">
        <xsl:apply-templates />
    </div>
</xsl:template>

<xsl:template match="inputgroupbtn">
    <div class="input-group-btn">
        <xsl:apply-templates />
    </div>
</xsl:template>

<xsl:template match="dbutton">
    <xsl:variable name="design">
        <xsl:choose>
            <xsl:when test="@design != ''">
                <xsl:value-of select="@design" />
            </xsl:when>
            <xsl:otherwise>default</xsl:otherwise>
        </xsl:choose>
    </xsl:variable>

    <xsl:variable name="size">
        <xsl:choose>
            <xsl:when test="@size != ''">
                btn-<xsl:value-of select="@size" />
            </xsl:when>
            <xsl:otherwise>btn-sm</xsl:otherwise>
        </xsl:choose>
    </xsl:variable>

    <buttongroup>
        <a class="btn btn-{$design} {x:iif($size, $size, '')} dropdown-toggle" data-toggle="dropdown">
            <xsl:choose>
                <xsl:when test="@iconfont != ''">
                    <i class="{@iconfont}"></i>
                    <xsl:if test="@text">
                        &#160;<xsl:value-of select="@text" />
                    </xsl:if>
                </xsl:when>
                <xsl:otherwise>
                    <xsl:value-of select="@text" />
                </xsl:otherwise>
            </xsl:choose>
            &#160;<span class="caret"></span>
        </a>
        <ul class="dropdown-menu" role="menu">
            <xsl:apply-templates />
        </ul>
    </buttongroup>
</xsl:template>

<xsl:template match="dbuttonitem">
    <xsl:variable name="onclickjs">
        <xsl:choose>
            <xsl:when test="@warning != ''">
                return Genesis.showWarning('<xsl:value-of select="@warning"/>',
                    '<xsl:value-of select="@id"/>',
                    <xsl:choose><xsl:when test="@cls != ''">, 
                    '<xsl:value-of select="@cls"/>'</xsl:when><xsl:otherwise>undefined</xsl:otherwise></xsl:choose><xsl:choose><xsl:when test="@onclick = 'form'">,
                    '<xsl:value-of select="@form" />', '<xsl:value-of select="@action" />'</xsl:when></xsl:choose>);
            </xsl:when>

            <xsl:when test="@onclick = 'form'">
                return Genesis.submit('<xsl:value-of select="@form" />', '<xsl:value-of select="@action" />', <xsl:value-of select="x:attr(@modal, 'false')" />);
            </xsl:when>

            <xsl:when test="@onclick = '' or not (@onclick)">
                <xsl:variable name="cls">
                    <xsl:choose>
                        <xsl:when test="@cls != ''">
                            <xsl:value-of select="@cls" />
                        </xsl:when>
                        <xsl:otherwise>
                            <xsl:value-of select="x:attr(@class, 'button')" />
                        </xsl:otherwise>
                    </xsl:choose>
                </xsl:variable>
                return Genesis.query('/handle/<xsl:value-of
                        select="$cls" />/click/<xsl:value-of
                        select="@id" />');
            </xsl:when>

            <xsl:otherwise>
                <xsl:value-of select="@onclick" />
            </xsl:otherwise>
        </xsl:choose>
    </xsl:variable>

    <li>
        <a href="{@href}" onclick="{$onclickjs}">
            <xsl:choose>
                <xsl:when test="@iconfont != ''">
                    <i class="{@iconfont}"></i>
                    <xsl:if test="@text">
                        &#160;<xsl:value-of select="@text" />
                    </xsl:if>
                </xsl:when>
                <xsl:otherwise>
                    <xsl:value-of select="@text" />
                </xsl:otherwise>
            </xsl:choose>
        </a>
    </li>
</xsl:template>

<xsl:template match="btn">
    <xsl:variable name="onclickjs">
        <xsl:choose>
            <xsl:when test="@warning != ''">
                return Genesis.showWarning('<xsl:value-of select="@warning"/>',
                    '<xsl:value-of select="@id"/>',
                    <xsl:choose><xsl:when test="@cls != ''">, 
                    '<xsl:value-of select="@cls"/>'</xsl:when><xsl:otherwise>undefined</xsl:otherwise></xsl:choose><xsl:choose><xsl:when test="@onclick = 'form'">,
                    '<xsl:value-of select="@form" />', '<xsl:value-of select="@action" />'</xsl:when></xsl:choose>);
            </xsl:when>

            <xsl:when test="@onclick = 'form'">
                return Genesis.submit('<xsl:value-of select="@form" />', '<xsl:value-of select="@action" />', <xsl:value-of select="x:attr(@modal, 'false')" />);
            </xsl:when>

            <xsl:when test="@onclick = '' or not (@onclick)">
                <xsl:variable name="cls">
                    <xsl:choose>
                        <xsl:when test="@cls != ''">
                            <xsl:value-of select="@cls" />
                        </xsl:when>
                        <xsl:otherwise>
                            <xsl:value-of select="x:attr(@class, 'button')" />
                        </xsl:otherwise>
                    </xsl:choose>
                </xsl:variable>
                return Genesis.query('/handle/<xsl:value-of
                        select="$cls" />/click/<xsl:value-of
                        select="@id" />');
            </xsl:when>

            <xsl:otherwise>
                <xsl:value-of select="@onclick" />
            </xsl:otherwise>
        </xsl:choose>
    </xsl:variable>

    <xsl:variable name="design">
        <xsl:choose>
            <xsl:when test="@design != ''">
                <xsl:value-of select="@design" />
            </xsl:when>
            <xsl:otherwise>default</xsl:otherwise>
        </xsl:choose>
    </xsl:variable>

    <xsl:variable name="size">
        <xsl:choose>
            <xsl:when test="@size != ''">
                btn-<xsl:value-of select="@size" />
            </xsl:when>
            <xsl:otherwise>btn-sm</xsl:otherwise>
        </xsl:choose>
    </xsl:variable>

    <a id="{@id}" href="{@href}" onclick="{$onclickjs}" class="btn btn-{$design} {x:iif($size, $size, '')}">
        <xsl:choose>
            <xsl:when test="@iconfont != ''">
                <i class="{@iconfont}"></i>
                <xsl:if test="@text">
                    &#160;<xsl:value-of select="@text" /><xsl:if test="@badge != ''">&#160;<span class="badge"><xsl:value-of select="@badge" /></span></xsl:if>
                </xsl:if>
            </xsl:when>
            <xsl:otherwise>
                <xsl:value-of select="@text" /><xsl:if test="@badge != ''">&#160;<span class="badge"><xsl:value-of select="@badge" /></span></xsl:if>
            </xsl:otherwise>
        </xsl:choose>
    </a>
</xsl:template>

<!-- End of button magic -->



<xsl:template match="linklabel">
    <a href="#" onclick="javascript:return Genesis.query('/handle/linklabel/click/{@id}');" class="ui-el-link" style="{x:iif(@bold, 'font-weight: bold;', '')}">
        <xsl:if test="@iconfont">
            <i class="{@iconfont}"></i>&#160;
        </xsl:if>
        <xsl:value-of select="@text" />
    </a>
</xsl:template>

<xsl:template match="linklabelredirect">
    <a href="#" onclick="javascript:Genesis.query('/handle/linklabel/click/{@id}');return Genesis.selectCategory('{@redirect}');" class="ui-el-link" style="{x:iif(@bold, 'font-weight: bold;', '')}">
        <xsl:if test="@iconfont">
            <i class="{@iconfont}"></i>&#160;
        </xsl:if>
        <xsl:value-of select="@text" />
    </a>
</xsl:template>

<xsl:template match="outlinklabel">
    <a href="{@url}" target="blank" class="ui-el-link">
        <xsl:if test="@iconfont">
            <i class="{@iconfont}"></i>&#160;
        </xsl:if>
        <xsl:value-of select="@text" />
    </a>
</xsl:template>

<xsl:template match="progressbar">
    <div class="progress">
        <div class="progress-bar" role="progressbar" aria-valuenow="{@value}" aria-valuemin="{@min}" aria-valuemax="{@max}" style="width: {@pct}%;">
            <xsl:value-of select="@rpct" />%
        </div>
    </div>
</xsl:template>

<xsl:template match="elementbox">
    <div class="ui-el-elementbox">
        <xsl:apply-templates />
    </div>
</xsl:template>





<xsl:template match="tooltip">
    <xsl:variable name="id" select="x:id(@id)" />
    <div style="display:inline-block; {@styles}" id="{$id}" class="ui-tooltip" data-toggle="tooltip" title="{x:jsesc(x:attr(@text, ''))}">
        <xsl:apply-templates />
    </div>
</xsl:template>

<xsl:template match="popover">
    <xsl:variable name="id" select="x:id(@id)" />
    <a id="{$id}" style="display:inline-block; {@styles}" class="pop-trigger {@class}" onclick="{@onclick}" href="#">
        <xsl:if test="@iconfont">
            <i class="{@iconfont}"></i>&#160;
        </xsl:if>
        <xsl:apply-templates />
    </a>
    <script>
        $('#<xsl:value-of select="$id" />').popover({
            animation: true,
            placement: '<xsl:value-of select="x:attr(@placement, 'right')" />',
            html: true,
            delayIn: <xsl:value-of select="x:attr(@delay, '0')" />,
            offset: <xsl:value-of select="x:attr(@offset, '0')" />,
            title: function() {
              return $("#<xsl:value-of select="$id" />-head").html();
            },
            content: function() {
              return $("#<xsl:value-of select="$id" />-content").html();
            },
            trigger: '<xsl:value-of select="x:attr(@trigger, 'click')" />',
        });
    </script>
</xsl:template>


<xsl:template match="popoverlink">
    <li><a class="popover-link" href="#" onclick="{@onclick}"><xsl:if test="@iconfont"><i class="{@iconfont}"></i></xsl:if>&#160;<xsl:value-of select="@text" /></a></li>
</xsl:template>


<xsl:template match="icon">
    <tooltip placement="above" text="{@text}"><image id="{@id}" file="{@icon}"/></tooltip>
</xsl:template>

<xsl:template match="iconfont">
    <tooltip placement="above" text="{@text}"><i class="{@iconfont}"></i></tooltip>
</xsl:template>

<xsl:template match="tipicon">
    <tooltip placement="above" text="{@text}"><btn id="{@id}" design="tipicon" cls="{@cls}" onclick="{@onclick}" warning="{@warning}" iconfont="{@iconfont}"/></tooltip>
</xsl:template>
