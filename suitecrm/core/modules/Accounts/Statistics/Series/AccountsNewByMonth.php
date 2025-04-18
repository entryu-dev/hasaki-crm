<?php
/**
 * SuiteCRM is a customer relationship management program developed by SalesAgility Ltd.
 * Copyright (C) 2021 SalesAgility Ltd.
 *
 * This program is free software; you can redistribute it and/or modify it under
 * the terms of the GNU Affero General Public License version 3 as published by the
 * Free Software Foundation with the addition of the following permission added
 * to Section 15 as permitted in Section 7(a): FOR ANY PART OF THE COVERED WORK
 * IN WHICH THE COPYRIGHT IS OWNED BY SALESAGILITY, SALESAGILITY DISCLAIMS THE
 * WARRANTY OF NON INFRINGEMENT OF THIRD PARTY RIGHTS.
 *
 * This program is distributed in the hope that it will be useful, but WITHOUT
 * ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
 * FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for more
 * details.
 *
 * You should have received a copy of the GNU Affero General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 *
 * In accordance with Section 7(b) of the GNU Affero General Public License
 * version 3, these Appropriate Legal Notices must retain the display of the
 * "Supercharged by SuiteCRM" logo. If the display of the logos is not reasonably
 * feasible for technical reasons, the Appropriate Legal Notices must display
 * the words "Supercharged by SuiteCRM".
 */

namespace App\Module\Accounts\Statistics\Series;

use App\Statistics\Entity\Statistic;
use App\Data\LegacyHandler\ListDataQueryHandler;
use App\Engine\LegacyHandler\LegacyHandler;
use App\Engine\LegacyHandler\LegacyScopeState;
use App\Statistics\Service\StatisticsProviderInterface;
use App\Statistics\StatisticsHandlingTrait;
use App\Statistics\Model\ChartOptions;
use App\Module\Service\ModuleNameMapperInterface;
use BeanFactory;
use SugarBean;
use Symfony\Component\HttpFoundation\RequestStack;

class AccountsNewByMonth extends LegacyHandler implements StatisticsProviderInterface
{
    use StatisticsHandlingTrait;

    public const KEY = 'accounts-new-by-month';

    /**
     * @var ListDataQueryHandler
     */
    private $queryHandler;

    /**
     * @var ModuleNameMapperInterface
     */
    private $moduleNameMapper;

    /**
     * LeadDaysOpen constructor.
     * @param string $projectDir
     * @param string $legacyDir
     * @param string $legacySessionName
     * @param string $defaultSessionName
     * @param LegacyScopeState $legacyScopeState
     * @param ListDataQueryHandler $queryHandler
     * @param ModuleNameMapperInterface $moduleNameMapper
     * @param RequestStack $requestStack
     */
    public function __construct(
        string $projectDir,
        string $legacyDir,
        string $legacySessionName,
        string $defaultSessionName,
        LegacyScopeState $legacyScopeState,
        ListDataQueryHandler $queryHandler,
        ModuleNameMapperInterface $moduleNameMapper,
        RequestStack $requestStack
    ) {
        parent::__construct($projectDir, $legacyDir, $legacySessionName, $defaultSessionName, $legacyScopeState, $requestStack);
        $this->queryHandler = $queryHandler;
        $this->moduleNameMapper = $moduleNameMapper;
    }

    /**
     * @inheritDoc
     */
    public function getHandlerKey(): string
    {
        return $this->getKey();
    }

    /**
     * @inheritDoc
     */
    public function getKey(): string
    {
        return self::KEY;
    }

    /**
     * @inheritDoc
     */
    public function getData(array $query): Statistic
    {
        [$module, $id, $criteria, $sort] = $this->extractContext($query);

        if (empty($module) || $module !== 'accounts') {
            return $this->getEmptySeriesResponse(self::KEY);
        }

        $this->init();
        $this->startLegacyApp();

        $legacyName = $this->moduleNameMapper->toLegacy($module);

        $bean = $this->getBean($legacyName);

        if (!$bean instanceof SugarBean) {
            return $this->getEmptySeriesResponse(self::KEY);
        }

        $query = $this->queryHandler->getQuery($bean, $criteria, $sort);
        $query = $this->generateQuery($query);

        $result = $this->runQuery($query, $bean);

        $nameField = 'yearmonth';
        $valueField = 'value';
        $groupingFields = '';
        $months = $this->getMonths();

        $series = $this->buildMultiSeries($result, $groupingFields, $nameField, $valueField, $months, true);

        $chartOptions = new ChartOptions();
        $chartOptions->yAxisTickFormatting = true;
        $chartOptions->xAxisTicks = $months;
        $chartOptions->legend = false;

        $statistic = $this->buildSeriesResponse(self::KEY, 'int', $series, $chartOptions);

        $this->close();

        return $statistic;
    }

    /**
     * @param string $legacyName
     * @return bool|SugarBean
     */
    protected function getBean(string $legacyName)
    {
        return BeanFactory::newBean($legacyName);
    }

    /**
     * @return array
     */
    protected function getMonths(): array
    {
        $currentDate = date('Y-m-d');
        $currentYear = date('Y', strtotime($currentDate));
        $currentMonth = date('n', strtotime($currentDate));

        $months = [];

        for ($i = 0; $i < 12; $i++) {
            $newMonth = $currentMonth - $i;

            if ($newMonth <= 0) {
                $newMonth += 12;
                $newYear = $currentYear - 1;
            } else {
                $newYear = $currentYear;
            }

            $months[] = $newYear . '-' . str_pad($newMonth, 2, '0', STR_PAD_LEFT);
        }
        return array_reverse($months);
    }

    /**
     * @param array $query
     * @param $bean
     * @return array
     */
    protected function runQuery(array $query, $bean): array
    {
        // send limit -2 to not add a limit
        return $this->queryHandler->runQuery($bean, $query, -1, -2);
    }

    /**
     * @param array $query
     * @return array
     */
    protected function generateQuery(array $query): array
    {
        $currentDate = date('Y-m-d');

        $nextMonth = date('Y-m-d', strtotime($currentDate . ' first day of next month'));
        $lastYear = date('Y-m-d', strtotime($nextMonth . ' -1 year'));

        $startDate = date('Y-m-d', strtotime($lastYear . ' -1 day'));
        $endDate = date('Y-m-d', strtotime($currentDate . ' +1 day'));

        $query['select'] = "SELECT COUNT(accounts.name) as value, CONCAT(EXTRACT(YEAR FROM accounts.date_entered), '-', LPAD(EXTRACT(MONTH FROM accounts.date_entered), 2, '0')) as yearmonth";
        $query['where'] .= " AND accounts.date_entered > '$startDate' AND accounts.date_entered < '$endDate' ";
        $query['order_by'] = '';
        $query['group_by'] = "GROUP BY yearmonth";

        return $query;
    }
}
